from setuptools import find_packages, setup
setup(
    name='tks-bot-framework',
    packages=find_packages
        (include=[
            'botframework', 'botframework.models', 'deployment.prod'
        ], 
        exclude=['tests*']), 
    include_package_data=True,   
    # version='0.1.0',
    # description='A bot framework for signal providers for Freya Alpha.',
    # author='Karin Richner, Brayan Svan',
    # license='copyright protected by Spark&Hale Robotic Industries',
    # install_requires=[],
    # setup_requires=['pytest-runner'],
    # tests_require=['pytest==4.4.1'],
    # test_suite='tests',
)