from setuptools import setup

setup(
    name='gait_analysis',
    version='0.1beta',
    packages=['gait_analysis', 'gait_analysis.cycle', 'gait_analysis.event', 'gait_analysis.utils',
              'gait_analysis.analysis', 'gait_analysis.modelling'],
    url='https://github.com/cereneo-foundation/gait_analysis',
    license='MIT License',
    author='boeni',
    author_email='andre.boeni@cereneo.foundation',
    description='This toolkit provide functionallities to postprocess motion capture data in c3d format.'
)
