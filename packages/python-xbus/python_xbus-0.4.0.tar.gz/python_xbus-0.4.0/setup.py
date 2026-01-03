import setuptools
import os
import subprocess

from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()


class protoc(setuptools.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import nrpc

        nrpc_dir = os.path.dirname(nrpc.__file__)
        import_path = os.path.dirname(nrpc_dir)
        subprocess.check_call(
            [
                "protoc",
                "--proto_path",
                "../xbus-api",
                "--proto_path",
                "../xbus-api/xbus",
                "--proto_path",
                "../xbus-api/tools/include",
                "--proto_path",
                import_path,
                "--python_out",
                ".",
                "--pynrpc_out",
                ".",
                "--pyi_out",
                ".",
                "../xbus-api/xbus/xbus.proto",
                "../xbus-api/xbus/control.proto",
            ]
        )


setup(
    name="python-xbus",
    version="0.4.0",
    url="https://bitbucket.org/orus-io/python-xbus",
    maintainer="xbus.io",
    maintainer_email="contact@xbus.io",
    description="A python client for Xbus (https://xbus.io)",
    long_description=long_description,
    cmdclass={"protoc": protoc},
    packages=["xbus", "xbus.demo"],
    entry_points={"console_scripts": ["xbus-python-client=xbus.cli:main"]},
    install_requires=["crccheck", "python-nrpc>=0.0.8", "pyyaml", "protobuf"],
)
