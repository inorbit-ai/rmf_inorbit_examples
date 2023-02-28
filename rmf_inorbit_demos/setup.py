from glob import glob
import os
from setuptools import setup

package_name = 'rmf_inorbit_demos'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name),
         glob('launch/*launch.[pxy][yma]*')),
        (os.path.join('share', package_name, 'warehouse'), glob('config/warehouse/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    author="Tomás Badenes tomasbadenes@gmail.com",
    maintainer='Julian Cerruti',
    maintainer_email='julian@inorbit.ai',
    description='Demo configuration package for rmf_inorbit_fleet_adapter',
    license='3-Clause BSD License',
    entry_points={
        'console_scripts': [
            'dispatch_loop=rmf_inorbit_demos.dispatch_loop:main'
        ],
    },
)
