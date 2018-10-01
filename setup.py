from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
import os


def _post_install(libname, libpath):
    from jumpscale import j
    # add this plugin to the config
    c = j.core.state.configGet('plugins', defval={})
    c[libname] = "%s/github/threefoldtech/0-robot/JumpscaleZrobot" % j.dirs.CODEDIR
    j.core.state.configSet('plugins', c)
    j.tools.jsloader.generate()


class install(_install):

    def run(self):
        _install.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath),
                     msg="Running post install task")


class develop(_develop):

    def run(self):
        _develop.run(self)
        libname = self.config_vars['dist_name']
        libpath = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), libname)
        self.execute(_post_install, (libname, libpath),
                     msg="Running post install task")


setup(
    name='ZeroRobot',
    version='0.8.0',
    description='Automation framework for cloud workloads',
    url='https://github.com/threefoldtech/0-robot',
    author='Christophe de Carvalho',
    author_email='christophe@gig.tech',
    license='Apache',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    install_requires=[
        'Jumpscale>=v9.3.1',
        'JumpscaleLib>=v9.3.1',
        'gevent>=1.2.2',
        'Flask>=0.12.2',
        'Flask-Inputs>=0.2.0',
        'Jinja2>=2.8',
        'MarkupSafe>=0.23',
        'Werkzeug>=0.11.4',
        'itsdangerous>=0.24',
        'jsonschema>=2.5.1',
        'six>=1.10.0',
        'python-jose>=2.0.1',
        'gevent >= 1.2.2',
        'psutil>=5.4.3',
        'prometheus_client>=0.1.1',
        'netifaces>=0.10.6',
        'msgpack-python>=0.4.8',
    ],
    scripts=['cmd/zrobot'],
    cmdclass={
        'install': install,
        'develop': develop,
        'development': develop,
    }
)
