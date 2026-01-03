from setuptools import setup,Extension
import os
from setuptools.command.build_ext import build_ext
from setuptools.extension import Extension
class CUDAExtension(Extension):
    def __init__(self, name, sources, *args, **kwargs):
        super().__init__(name, sources, *args, **kwargs)

class CUDACompiler(build_ext):
    def build_extension(self, ext):
        if isinstance(ext, CUDAExtension):
            host_compiler = os.getenv('HOST_COMPILER', 'cl')  # 默认使用MSVC的cl
            obj_path = self.get_ext_fullpath(ext.name)
            src_path = ext.sources[0]
            cmd = ['nvcc','--shared','-Xcompiler', '/MD', '-Xcompiler', '/LD','-m64',
                   '-I',self.get_include_path(),'-I',self.get_cuda_include_path(),'-L',self.get_cuda_lib_path(),'-L',self.get_link_path(),'-lcudart','-o', obj_path, src_path]
            if host_compiler == 'gcc':
                cmd = ['nvcc', '--shared', '-Xcompiler', '/MD', '-Xcompiler', '/LD', '-m64', '-I',
                       self.get_include_path(), '-I', self.get_cuda_include_path(), '-L', self.get_cuda_lib_path(),
                       '-L', self.get_link_path(), '-lcudart', '-o', obj_path, src_path]
            self.spawn(cmd)
        else:
            super().build_extension(ext)
    def get_include_path(self):
        import os
        all_path=os.getenv("path")
        split_path=all_path.split(sep=";")
        for item in split_path:
            if item.endswith("\\"):
                pass
            else:
                item=item+"\\"
            if os.path.exists(path=item+"\\include\\"):
                return item+"include"
        return None
    def get_cuda_include_path(self):
        path=os.getenv("CUDA_HOME")
        if path==None:
            raise RuntimeError("Not Found CUDA_HOME path!")
        return path+"include"
    def get_cuda_lib_path(self):
        path = os.getenv("CUDA_HOME")
        if path == None:
            raise RuntimeError("Not Found CUDA_HOME path!")
        return path + "lib\\x64"
    def get_link_path(self):
        import os
        all_path = os.getenv("path")
        split_path = all_path.split(sep=";")
        for item in split_path:
            if item.endswith("\\"):
                pass
            else:
                item=item+"\\"
            if os.path.exists(path=item+"\\libs\\"):
                return item+"libs"
        return None
DevicePropertiesModule=CUDAExtension(
    name="GpuCalculateTools._GPUDeviceDiagnose",
    sources=['GpuCalculateTools/includes/device_diagnose/device_properties.cu'])
DeviceTestModule=CUDAExtension(
    name="GpuCalculateTools._GPUDeviceTest",
    sources=['GpuCalculateTools/includes/device_test/device_test_array.cu']
)
readme=open('README.md','r',encoding='utf-8')
setup(
    name="gpucalculatetools",
    version="0.0.3",
    author="adroit_fisherman",
    author_email="1295284735@qq.com",
    platforms="Windows",
    description="GpuCalculateTools is a data computation library developed based on the native Python C API and CUDA. Currently, the library is in testing and development. If you have any questions, please contact 1295284735@qq.com.",
    long_description_content_type="text/markdown",
    long_description=readme.read(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Natural Language :: Chinese (Simplified)",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Programming Language :: C++",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities"
    ],
    include_package_data=True,
    packages=['GpuCalculateTools.GPUImplements'],
    ext_modules=[
        DevicePropertiesModule,
        DeviceTestModule
    ],
    cmdclass={"build_ext":CUDACompiler},
    python_requires=">=3.6"
)
readme.close()