import math
from pathlib import Path
import xml.etree.ElementTree as ET

from conftest import PACKAGE_DIR
from conftest import run_bash


def test_basket_layout_a_xacro_expands_to_valid_urdf(tmp_path: Path) -> None:
    urdf_path = tmp_path / 'basket_layout_a.urdf'
    xacro_path = PACKAGE_DIR / 'urdf' / 'model_basket_layout_a.xacro'

    result = run_bash(f'xacro "{xacro_path}" > "{urdf_path}" && check_urdf "{urdf_path}"')
    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    expanded = urdf_path.read_text(encoding='utf-8')
    assert 'rbvogui_basket_root_link' in expanded
    assert 'rbvogui_front_top_lidar_root_link' in expanded
    assert 'rbvogui_back_top_lidar_root_link' in expanded
    assert 'rbvogui_ublox_ann_mb_00_00_left_root_link' in expanded
    assert 'rbvogui_ublox_ann_mb_00_00_right_root_link' in expanded
    assert 'fork_root_link' not in expanded

    root = ET.parse(urdf_path).getroot()
    expected_poses = {
        'rbvogui_ublox_ann_mb_00_00_left_root_joint': (0.257925, math.pi / 2.0),
        'rbvogui_ublox_ann_mb_00_00_right_root_joint': (-0.257925, -math.pi / 2.0),
    }
    for joint_name, (expected_y, expected_yaw) in expected_poses.items():
        joint = root.find(f"joint[@name='{joint_name}']")
        assert joint is not None
        assert joint.find('parent').attrib['link'] == 'rbvogui_basket_root_link'
        origin = joint.find('origin')
        xyz = tuple(float(value) for value in origin.attrib['xyz'].split())
        rpy = tuple(float(value) for value in origin.attrib['rpy'].split())
        assert xyz == (0.371719, expected_y, 0.664886)
        assert rpy == (0.0, 0.0, expected_yaw)

        data_joint_name = joint_name.replace('_root_joint', '_joint')
        data_joint = root.find(f"joint[@name='{data_joint_name}']")
        assert data_joint is not None
        assert data_joint.find('origin').attrib == {'rpy': '0 0 0', 'xyz': '0 0 0'}


def test_basket_layout_a_simulation_xacro_expands_to_valid_urdf(tmp_path: Path) -> None:
    urdf_path = tmp_path / 'basket_layout_a_simulation.urdf'
    xacro_path = PACKAGE_DIR / 'urdf' / 'model_basket_layout_a.xacro'
    sim_path = PACKAGE_DIR / 'config' / 'default_simulation.yaml'

    result = run_bash(
        f'xacro "{xacro_path}" sim_file:="{sim_path}" > "{urdf_path}" && check_urdf "{urdf_path}"'
    )
    output = result.stdout + result.stderr

    assert result.returncode == 0, output
    expanded = urdf_path.read_text(encoding='utf-8')
    assert 'front_top_lidar/scan' in expanded
    assert 'back_top_lidar/scan' in expanded
    assert 'sensor type="navsat"' not in expanded
    assert 'front_bottom_lidar' not in expanded
    assert 'fork_root_joint' not in expanded
