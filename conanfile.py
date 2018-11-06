from conans import ConanFile, CMake, tools, AutoToolsBuildEnvironment
import os

class WavpackConan(ConanFile):
    name = "wavpack"
    version = "5.1.0"
    description = "WavPack is a completely open audio compression format providing lossless, high-quality lossy, and a unique hybrid compression mode"
    url = "https://github.com/conanos/wavpack"
    license = "BSD_like"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = "shared=True"
    generators = "cmake"

    source_subfolder = "source_subfolder"
    
    def source(self):
        url_ = 'https://github.com/dbry/WavPack/archive/%s.tar.gz'%(self.version)
        tools.get(url_)
        extracted_dir = "WavPack-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        with tools.chdir(self.source_subfolder):
            self.run("autoreconf -f -i")

            autotools = AutoToolsBuildEnvironment(self)
            _args = ["--prefix=%s/builddir"%(os.getcwd()), "--disable-apps"]
            if self.options.shared:
                _args.extend(['--enable-shared=yes','--enable-static=no'])
            else:
                _args.extend(['--enable-shared=no','--enable-static=yes'])
            autotools.configure(args=_args)
            autotools.make(args=["-j4"])
            autotools.install()

    def package(self):
        if tools.os_info.is_linux:
            with tools.chdir(self.source_subfolder):
                self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

