"""
MeshCat-based 3D visualizer for SRMP (Search-based Robot Motion Planning)

This module provides visualization capabilities for robots, collision objects,
and trajectory animations using MeshCat.

Example usage:
    from srmp.visualizer import VisualPlannerInterface

    # Create planner with visualization
    planner = VisualPlannerInterface()
    planner.add_articulation("panda", "panda_hand", urdf_path, srdf_path)
    planner.add_box("table", size=[1, 1, 0.05], pose=pose)

    # Display everything automatically
    planner.visualize()

    # Animate trajectory
    planner.animate_trajectory(trajectories)
"""

import numpy as np
import meshcat
import meshcat.geometry as g
import meshcat.transformations as tf
from typing import Optional, List, Dict, Union, Tuple
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from srmp.planner_interface import PlannerInterface
import ims.pyims as pyims


class VisualPlannerInterface(PlannerInterface):
    """
    PlannerInterface with automatic MeshCat visualization.

    Inherits from PlannerInterface to get all planning functionality including read_sim(),
    and adds automatic tracking and visualization of the scene.
    """

    def __init__(self, zmq_url: Optional[str] = None):
        """
        Initialize visual planner interface.

        Args:
            zmq_url: Optional ZMQ URL for MeshCat server (default: None for auto)
        """
        # Initialize parent PlannerInterface
        super().__init__()

        # Visualization setup
        self._vis: Optional[meshcat.Visualizer] = None
        self._zmq_url = zmq_url

        # Track what's been added
        self._robots: Dict[str, Dict] = {}  # name -> {urdf_path, srdf_path, end_effector, ...}
        self._objects: Dict[str, Dict] = {}  # name -> {type, params, pose}
        self._robot_links: Dict[str, List[str]] = {}  # name -> list of link names with visuals
        self._attached_objects: Dict[str, Dict] = {}  # object_name -> {art_name, link_id, link_name}

        print("Visual Planner Interface created.")
        print("Call .visualize() to open the 3D viewer after adding robots/objects.")

    # Override parent methods to track what's added for visualization

    def add_articulation(self, name: str, end_effector: str, urdf_path: str,
                        srdf_path: str = "", link_names: List[str] = [],
                        joint_names: List[str] = [], gravity: np.ndarray = np.array([0, 0, 0]),
                        planned: bool = True) -> None:
        """Add articulation and track it for visualization."""
        super().add_articulation(
            name=name,
            end_effector=end_effector,
            urdf_path=urdf_path,
            srdf_path=srdf_path,
            link_names=link_names,
            joint_names=joint_names,
            gravity=gravity,
            planned=planned
        )

        self._robots[name] = {
            'urdf_path': urdf_path,
            'srdf_path': srdf_path,
            'end_effector': end_effector,
            'planned': planned
        }

    def add_box(self, name: str, size: np.ndarray, pose: pyims.Pose = None) -> None:
        """Add box and track it for visualization."""
        if pose is None:
            pose = pyims.Pose()
        super().add_box(name, size, pose)

        self._objects[name] = {
            'type': 'box',
            'size': size.copy(),
            'pose': {'p': pose.p.copy(), 'q': pose.q.copy()}
        }

    def add_sphere(self, name: str, radius: float, pose: pyims.Pose = None) -> None:
        """Add sphere and track it for visualization."""
        if pose is None:
            pose = pyims.Pose()
        super().add_sphere(name, radius, pose)

        self._objects[name] = {
            'type': 'sphere',
            'radius': radius,
            'pose': {'p': pose.p.copy(), 'q': pose.q.copy()}
        }

    def add_cylinder(self, name: str, radius: float, height: float, pose: pyims.Pose = None) -> None:
        """Add cylinder and track it for visualization."""
        if pose is None:
            pose = pyims.Pose()
        super().add_cylinder(name, radius, height, pose)

        self._objects[name] = {
            'type': 'cylinder',
            'radius': radius,
            'height': height,
            'pose': {'p': pose.p.copy(), 'q': pose.q.copy()}
        }

    def add_mesh(self, name: str, mesh_path: str = None,
                 vertices: np.ndarray = None, triangles: np.ndarray = None,
                 scale: np.ndarray = np.ones(3), pose = None, convex: bool = False) -> None:
        """
        Add mesh and track it for visualization.

        Args:
            name: Object name
            mesh_path: Path to mesh file (mutually exclusive with vertices/triangles)
            vertices: Mesh vertices as Nx3 array (requires triangles)
            triangles: Mesh triangles as Mx3 array of indices (requires vertices)
            scale: Scale factor for mesh
            pose: Pose of the mesh
            convex: Whether to treat mesh as convex (only for file-based meshes)
        """
        if pose is None:
            pose = pyims.Pose()

        # Call correct overload based on whether we have vertices/triangles or mesh_path
        if vertices is not None and triangles is not None:
            # Use vertices/triangles overload (no convex parameter)
            super().add_mesh(name, vertices, triangles, scale=scale, pose=pose)
        elif mesh_path is not None:
            # Use mesh_path overload
            super().add_mesh(name, mesh_path, scale=scale, pose=pose, convex=convex)
        else:
            raise ValueError("Must provide either mesh_path or both vertices and triangles")

        # Track for visualization
        mesh_info = {
            'type': 'mesh',
            'scale': scale.copy() if isinstance(scale, np.ndarray) else np.array(scale),
            'pose': {'p': pose.p.copy(), 'q': pose.q.copy()},
            'convex': convex
        }

        if mesh_path is not None:
            mesh_info['mesh_path'] = mesh_path
        if vertices is not None and triangles is not None:
            mesh_info['vertices'] = vertices.copy()
            mesh_info['triangles'] = triangles.copy()

        self._objects[name] = mesh_info

    def remove_object(self, name: str) -> None:
        """Remove object and stop tracking it."""
        super().remove_object(name)
        if name in self._objects:
            del self._objects[name]
            if self._vis is not None:
                self._vis[f"objects/{name}"].delete()

    def remove_articulation(self, name: str) -> None:
        """Remove articulation and stop tracking it."""
        super().remove_articulation(name)
        if name in self._robots:
            del self._robots[name]
            if self._vis is not None:
                self._vis[f"robots/{name}"].delete()

    def set_base_pose(self, name: str, pose: pyims.Pose) -> None:
        """Set base pose and update visualization."""
        super().set_base_pose(name, pose)
        if self._vis is not None and name in self._robot_links:
            self._update_robot_visual_poses(name)

    def set_qpos(self, name: str, qpos: np.ndarray) -> None:
        """Set joint positions and update visualization."""
        super().set_qpos(name, qpos)
        if self._vis is not None and name in self._robot_links:
            self._update_robot_visual_poses(name)

    def set_qpos_all(self, state: np.ndarray) -> None:
        """Set joint positions for all planned articulations and update visualization."""
        super().set_qpos_all(state)
        if self._vis is not None:
            for name in self._robots.keys():
                if name in self._robot_links:
                    self._update_robot_visual_poses(name)

    def attach_object(self, name: str, art_name: str, link_id: int,
                      touch_links: Optional[List[str]] = None) -> None:
        """
        Attach object to robot link.

        The object will move with the robot link in visualization.
        """
        if touch_links is None:
            super().attach_object(name, art_name, link_id)
        else:
            super().attach_object(name, art_name, link_id, touch_links)

        # Get link name from link_id
        link_name = self._get_link_name_from_id(art_name, link_id)

        if link_name is not None and name in self._objects:
            # Get current link pose
            link_pose = self.get_link_pose(art_name, link_name)

            # Get current object pose
            obj_info = self._objects[name]
            obj_p = obj_info['pose']['p']
            obj_q = obj_info['pose']['q']

            # Compute relative transform: link^-1 * object
            # Convert poses to transformation matrices
            T_link = self._pose_to_transform(link_pose.p, link_pose.q)
            T_obj = self._pose_to_transform(obj_p, obj_q)

            # Compute relative transform
            T_link_inv = np.linalg.inv(T_link)
            T_relative = T_link_inv @ T_obj

            # Extract relative pose
            relative_p = T_relative[0:3, 3]
            relative_q = tf.quaternion_from_matrix(T_relative)

            # Track attachment with relative pose
            self._attached_objects[name] = {
                'art_name': art_name,
                'link_id': link_id,
                'link_name': link_name,
                'relative_p': relative_p,
                'relative_q': relative_q
            }
        else:
            # Fallback: just track attachment without relative pose
            self._attached_objects[name] = {
                'art_name': art_name,
                'link_id': link_id
            }

    def detach_object(self, name: str, also_remove: bool = False) -> bool:
        """Detach object from robot."""
        result = super().detach_object(name, also_remove)

        # Remove from attached objects tracking
        if name in self._attached_objects:
            del self._attached_objects[name]

        if also_remove and name in self._objects:
            del self._objects[name]
            if self._vis is not None:
                self._vis[f"objects/{name}"].delete()
        elif name in self._objects and self._vis is not None:
            # Re-visualize at current pose if not removing
            self._add_object_visual(name, self._objects[name])

        return result

    def detach_all_objects(self, also_remove: bool = False) -> bool:
        """Detach all attached objects."""
        result = super().detach_all_objects(also_remove)

        # Clear attached objects tracking
        attached_names = list(self._attached_objects.keys())
        self._attached_objects.clear()

        if also_remove:
            if self._vis is not None:
                for name in list(self._objects.keys()):
                    self._vis[f"objects/{name}"].delete()
            self._objects.clear()
        else:
            # Re-visualize detached objects at their current poses
            if self._vis is not None:
                for name in attached_names:
                    if name in self._objects:
                        self._add_object_visual(name, self._objects[name])

        return result

    def reset(self, reset_robots: bool = True) -> None:
        """Reset planner and optionally clear visualization."""
        super().reset(reset_robots)
        if reset_robots:
            self._robots.clear()
            self._objects.clear()
            self._robot_links.clear()
            self._attached_objects.clear()
            if self._vis is not None:
                self._vis.delete()

    def visualize(self, open_browser: bool = True) -> None:
        """
        Open MeshCat visualizer and display the current scene.

        Args:
            open_browser: Whether to print URL for opening in browser
        """
        if self._vis is None:
            self._vis = meshcat.Visualizer(zmq_url=self._zmq_url)

            if open_browser:
                print(f"\n{'='*60}")
                print("MeshCat Visualizer Started!")
                print(f"{'='*60}")
                print(f"Open this URL in your browser:\n  {self._vis.url()}")
                print(f"{'='*60}\n")

        # Clear and redraw everything
        self._vis.delete()

        # Add robots
        for name, info in self._robots.items():
            self._add_robot_visual(name, info['urdf_path'])
            # Update robot to current configuration
            self._update_robot_visual_poses(name)

        # Add objects
        for name, info in self._objects.items():
            self._add_object_visual(name, info)

    def _add_robot_visual(self, name: str, urdf_path: str, color: int = 0xffa500) -> None:
        """Load and display robot from URDF."""
        # Track links with visuals
        self._robot_links[name] = []

        try:
            tree = ET.parse(urdf_path)
            root = tree.getroot()
            urdf_dir = Path(urdf_path).parent

            print(f"Loading robot '{name}' from {urdf_path}")

            for link in root.findall('link'):
                link_name = link.get('name')
                visual = link.find('visual')

                if visual is None:
                    continue

                geometry = visual.find('geometry')
                if geometry is None:
                    continue

                # Get visual origin
                origin = visual.find('origin')
                xyz = [0, 0, 0]
                rpy = [0, 0, 0]
                if origin is not None:
                    xyz_str = origin.get('xyz', '0 0 0')
                    rpy_str = origin.get('rpy', '0 0 0')
                    xyz = [float(x) for x in xyz_str.split()]
                    rpy = [float(x) for x in rpy_str.split()]

                # Get material color from URDF
                link_color = self._get_urdf_color(visual, root, default_color=color)

                path = f"robots/{name}/{link_name}"

                # Handle meshes
                mesh_elem = geometry.find('mesh')
                if mesh_elem is not None:
                    mesh_filename = mesh_elem.get('filename')

                    # Resolve mesh path
                    if mesh_filename.startswith('package://'):
                        parts = mesh_filename.replace('package://', '').split('/', 1)
                        mesh_path = urdf_dir / parts[1] if len(parts) > 1 else urdf_dir / mesh_filename
                    elif mesh_filename.startswith('file://'):
                        mesh_path = Path(mesh_filename.replace('file://', ''))
                    else:
                        mesh_path = urdf_dir / mesh_filename

                    if mesh_path.exists():
                        scale_str = mesh_elem.get('scale', '1 1 1')
                        scale = [float(x) for x in scale_str.split()]

                        # Load mesh based on file extension
                        mesh_ext = mesh_path.suffix.lower()
                        if mesh_ext == '.dae':
                            mesh_geom = g.DaeMeshGeometry.from_file(str(mesh_path))
                        elif mesh_ext == '.obj':
                            mesh_geom = g.ObjMeshGeometry.from_file(str(mesh_path))
                        else:  # .stl or others
                            mesh_geom = g.StlMeshGeometry.from_file(str(mesh_path))

                        material = g.MeshLambertMaterial(color=link_color)

                        T = self._rpy_xyz_to_transform(xyz, rpy)
                        scale_mat = np.diag([*scale, 1.0])
                        T = T @ scale_mat

                        self._vis[path].set_object(mesh_geom, material)
                        self._vis[path].set_transform(T)
                        self._robot_links[name].append(link_name)
                        print(f"  Added mesh for link '{link_name}'")

                # Handle primitives
                box_elem = geometry.find('box')
                if box_elem is not None:
                    size = [float(x) for x in box_elem.get('size').split()]
                    box_geom = g.Box(size)
                    material = g.MeshLambertMaterial(color=color)
                    T = self._rpy_xyz_to_transform(xyz, rpy)
                    self._vis[path].set_object(box_geom, material)
                    self._vis[path].set_transform(T)
                    self._robot_links[name].append(link_name)

                sphere_elem = geometry.find('sphere')
                if sphere_elem is not None:
                    radius = float(sphere_elem.get('radius'))
                    sphere_geom = g.Sphere(radius)
                    material = g.MeshLambertMaterial(color=color)
                    T = tf.translation_matrix(xyz)
                    self._vis[path].set_object(sphere_geom, material)
                    self._vis[path].set_transform(T)
                    self._robot_links[name].append(link_name)

                cylinder_elem = geometry.find('cylinder')
                if cylinder_elem is not None:
                    radius = float(cylinder_elem.get('radius'))
                    length = float(cylinder_elem.get('length'))
                    cylinder_geom = g.Cylinder(length, radius)
                    material = g.MeshLambertMaterial(color=color)
                    T = self._rpy_xyz_to_transform(xyz, rpy)
                    self._vis[path].set_object(cylinder_geom, material)
                    self._vis[path].set_transform(T)
                    self._robot_links[name].append(link_name)

            print(f"Finished loading robot '{name}': {len(self._robot_links[name])} links with visuals")

        except Exception as e:
            print(f"Warning: Could not load robot {name}: {e}")

    def _add_object_visual(self, name: str, info: Dict) -> None:
        """Add collision object visualization."""
        path = f"objects/{name}"
        pose_info = info['pose']
        position = pose_info['p']
        quaternion = pose_info['q']

        try:
            if info['type'] == 'box':
                box_geom = g.Box(info['size'])
                material = g.MeshLambertMaterial(color=0x88aa88, opacity=0.7, transparent=True)
                T = self._pose_to_transform(position, quaternion)
                self._vis[path].set_object(box_geom, material)
                self._vis[path].set_transform(T)

            elif info['type'] == 'sphere':
                sphere_geom = g.Sphere(info['radius'])
                material = g.MeshLambertMaterial(color=0x8888ff, opacity=0.7, transparent=True)
                T = tf.translation_matrix(position)
                self._vis[path].set_object(sphere_geom, material)
                self._vis[path].set_transform(T)

            elif info['type'] == 'cylinder':
                cylinder_geom = g.Cylinder(info['height'], info['radius'])
                material = g.MeshLambertMaterial(color=0xff8888, opacity=0.7, transparent=True)
                T = self._pose_to_transform(position, quaternion)
                self._vis[path].set_object(cylinder_geom, material)
                self._vis[path].set_transform(T)

            elif info['type'] == 'mesh':
                # Check if mesh is defined by vertices/triangles or file path
                if 'vertices' in info and 'triangles' in info:
                    # Procedural mesh from vertices and triangles
                    mesh_geom = g.TriangularMeshGeometry(info['vertices'], info['triangles'])
                elif 'mesh_path' in info:
                    # File-based mesh
                    mesh_path = Path(info['mesh_path'])
                    mesh_ext = mesh_path.suffix.lower()
                    if mesh_ext == '.dae':
                        mesh_geom = g.DaeMeshGeometry.from_file(info['mesh_path'])
                    elif mesh_ext == '.obj':
                        mesh_geom = g.ObjMeshGeometry.from_file(info['mesh_path'])
                    else:  # .stl or others
                        mesh_geom = g.StlMeshGeometry.from_file(info['mesh_path'])
                else:
                    print(f"Warning: Mesh {name} has no vertices/triangles or mesh_path")
                    return

                material = g.MeshLambertMaterial(color=0xcccccc, opacity=0.8, transparent=True)
                T = self._pose_to_transform(position, quaternion)
                scale_mat = np.diag([*info['scale'], 1.0])
                T = T @ scale_mat
                self._vis[path].set_object(mesh_geom, material)
                self._vis[path].set_transform(T)

        except Exception as e:
            print(f"Warning: Could not visualize object {name}: {e}")

    def _update_robot_visual_poses(self, robot_name: str) -> None:
        """Update all link transforms to their current poses from the planner."""
        if robot_name not in self._robot_links:
            return

        print(f"Updating {len(self._robot_links[robot_name])} link poses for robot '{robot_name}'")

        for link_name in self._robot_links[robot_name]:
            try:
                # Get current link pose from planner
                link_pose = self.get_link_pose(robot_name, link_name)

                # Convert to transform matrix and update MeshCat
                T = self._pose_to_transform(link_pose.p, link_pose.q)
                path = f"robots/{robot_name}/{link_name}"
                self._vis[path].set_transform(T)

            except Exception as e:
                print(f"  Warning: Could not update link '{link_name}': {e}")

        # Update attached objects for this robot
        for obj_name, attachment_info in self._attached_objects.items():
            if attachment_info['art_name'] == robot_name:
                self._update_attached_object_visual(obj_name)

    def _update_attached_object_visual(self, obj_name: str) -> None:
        """Update visualization of an attached object to follow its attachment link."""
        if obj_name not in self._attached_objects or obj_name not in self._objects:
            return

        attachment_info = self._attached_objects[obj_name]

        # Check if we have relative pose information
        if 'link_name' not in attachment_info or 'relative_p' not in attachment_info:
            return

        art_name = attachment_info['art_name']
        link_name = attachment_info['link_name']

        try:
            # Get current link pose
            link_pose = self.get_link_pose(art_name, link_name)
            T_link = self._pose_to_transform(link_pose.p, link_pose.q)

            # Get relative transform
            T_relative = self._pose_to_transform(
                attachment_info['relative_p'],
                attachment_info['relative_q']
            )

            # Compute object's world pose: link * relative
            T_obj = T_link @ T_relative

            # Extract position and quaternion
            obj_p = T_obj[0:3, 3]
            obj_q = tf.quaternion_from_matrix(T_obj)

            # Update object info
            obj_info = self._objects[obj_name]
            obj_info['pose']['p'] = obj_p.copy()
            obj_info['pose']['q'] = obj_q.copy()

            # Update visualization
            path = f"objects/{obj_name}"
            T = self._pose_to_transform(obj_p, obj_q)

            # Apply scale for meshes
            if obj_info['type'] == 'mesh' and 'scale' in obj_info:
                scale_mat = np.diag([*obj_info['scale'], 1.0])
                T = T @ scale_mat

            self._vis[path].set_transform(T)

        except Exception as e:
            print(f"  Warning: Could not update attached object '{obj_name}': {e}")

    def animate_trajectory(self, trajectories: Union[Dict[str, pyims.Trajectory], pyims.Trajectory],
                          dt: float = 0.05, robot_name: Optional[str] = None) -> None:
        """
        Animate trajectory by updating robot configurations.

        Args:
            trajectories: Either a dict of {robot_name: trajectory} or single Trajectory
            dt: Time step between frames (seconds)
            robot_name: Robot name if single trajectory provided
        """
        if self._vis is None:
            print("Please call .visualize() first to open the viewer!")
            return

        # Handle single trajectory
        if not isinstance(trajectories, dict):
            if robot_name is None:
                robot_name = list(self._robots.keys())[0] if self._robots else None
            if robot_name is None:
                print("Error: No robot specified and no robots in scene")
                return
            trajectories = {robot_name: trajectories}

        # Get max length
        max_len = max(len(traj.positions) for traj in trajectories.values())

        print(f"Animating {len(trajectories)} robot(s) for {max_len} waypoints...")

        for i in range(max_len):
            for robot_name, traj in trajectories.items():
                if i < len(traj.positions):
                    q = traj.positions[i]
                    self.set_qpos(robot_name, np.array(q))

                    # Update link transforms in MeshCat
                    if robot_name in self._robot_links:
                        for link_name in self._robot_links[robot_name]:
                            try:
                                # Get updated link pose from planner
                                link_pose = self.get_link_pose(robot_name, link_name)

                                # Convert to transform matrix and update MeshCat
                                T = self._pose_to_transform(link_pose.p, link_pose.q)
                                path = f"robots/{robot_name}/{link_name}"
                                self._vis[path].set_transform(T)
                            except Exception as e:
                                # Skip links that can't be updated
                                pass

            time.sleep(dt)

            if i % 20 == 0:
                print(f"  Frame {i}/{max_len}")

        print("Animation complete!")

    def _get_urdf_color(self, visual, root, default_color: int = 0xffa500) -> int:
        """Extract color from URDF material definition."""
        material_elem = visual.find('material')
        if material_elem is None:
            return default_color

        # Try to get color from inline definition
        color_elem = material_elem.find('color')
        if color_elem is not None:
            rgba_str = color_elem.get('rgba')
            if rgba_str:
                rgba = [float(x) for x in rgba_str.split()]
                # Convert RGBA (0-1) to hex color
                r, g, b = rgba[:3]
                return int(r * 255) << 16 | int(g * 255) << 8 | int(b * 255)

        # Try to get color from material name reference
        mat_name = material_elem.get('name')
        if mat_name:
            # Search for material definition in root
            for mat_def in root.findall('material'):
                if mat_def.get('name') == mat_name:
                    color_elem = mat_def.find('color')
                    if color_elem is not None:
                        rgba_str = color_elem.get('rgba')
                        if rgba_str:
                            rgba = [float(x) for x in rgba_str.split()]
                            r, g, b = rgba[:3]
                            return int(r * 255) << 16 | int(g * 255) << 8 | int(b * 255)

        return default_color

    def _pose_to_transform(self, position: np.ndarray, quaternion: np.ndarray) -> np.ndarray:
        """Convert position and quaternion to 4x4 transformation matrix."""
        w, x, y, z = quaternion
        R = tf.quaternion_matrix([w, x, y, z])
        R[0:3, 3] = position
        return R

    def _rpy_xyz_to_transform(self, xyz: List[float], rpy: List[float]) -> np.ndarray:
        """Convert XYZ position and RPY orientation to 4x4 transformation matrix."""
        roll, pitch, yaw = rpy
        R = tf.euler_matrix(roll, pitch, yaw, 'sxyz')
        R[0:3, 3] = xyz
        return R

    def _get_link_name_from_id(self, art_name: str, link_id: int) -> Optional[str]:
        """
        Get link name from link ID by parsing the URDF.

        Args:
            art_name: Articulation name
            link_id: Link ID (index)

        Returns:
            Link name if found, None otherwise
        """
        if art_name not in self._robots:
            return None

        urdf_path = self._robots[art_name]['urdf_path']

        try:
            tree = ET.parse(urdf_path)
            root = tree.getroot()

            # Get all link elements in order
            links = root.findall('link')

            # Return the link name at the specified index
            if 0 <= link_id < len(links):
                return links[link_id].get('name')

        except Exception as e:
            print(f"Warning: Could not parse URDF to get link name: {e}")

        return None

    @property
    def url(self):
        """Get the MeshCat visualizer URL."""
        if self._vis is None:
            return "Visualizer not started. Call .visualize() first."
        return self._vis.url()


