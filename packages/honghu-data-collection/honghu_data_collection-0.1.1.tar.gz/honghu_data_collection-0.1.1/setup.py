from setuptools import setup

setup(
    name='honghu_data_collection',
    version='0.1.1',
    author='xuzhaocai',
    description='红湖·数据汇聚管理平台PYTHON SDK',
    py_modules=['data_collection_tool'],
    install_requires=[
        'requests>=2.25.1',
    ],
    python_requires='>=3.6',
)