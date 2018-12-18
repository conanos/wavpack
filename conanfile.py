from conans import ConanFile, tools, AutoToolsBuildEnvironment, MSBuild
from conanos.build import config_scheme
import os, shutil

class WavpackConan(ConanFile):
    name = "wavpack"
    version = "5.1.0"
    description = "WavPack is a completely open audio compression format providing lossless, high-quality lossy, and a unique hybrid compression mode"
    url = "https://github.com/conanos/wavpack"
    homepage = "http://www.wavpack.com/"
    license = "BSD"
    patch = "msvc-afxres-h-not-existing.patch"
    exports = ["COPYING", patch]
    generators = "visual_studio", "gcc"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = { 'shared': True, 'fPIC': True }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        del self.settings.compiler.libcxx

        config_scheme(self)

    def source(self):
        url_ = 'https://github.com/dbry/WavPack/archive/{version}.tar.gz'
        tools.get(url_.format(version=self.version))
        extracted_dir = "WavPack-" + self.version
        if self.settings.os == 'Windows':
            tools.patch(patch_file=self.patch)
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        #with tools.chdir(self.source_subfolder):
        #    self.run("autoreconf -f -i")

        #    autotools = AutoToolsBuildEnvironment(self)
        #    _args = ["--prefix=%s/builddir"%(os.getcwd()), "--disable-apps"]
        #    if self.options.shared:
        #        _args.extend(['--enable-shared=yes','--enable-static=no'])
        #    else:
        #        _args.extend(['--enable-shared=no','--enable-static=yes'])
        #    autotools.configure(args=_args)
        #    autotools.make(args=["-j4"])
        #    autotools.install()

        if self.settings.os == 'Windows':
            with tools.chdir(os.path.join(self._source_subfolder)):
                msbuild = MSBuild(self)
                msbuild.build("wavpack.sln",upgrade_project=True,platforms={'x86': 'Win32', 'x86_64': 'x64'})


    def package(self):
        if self.settings.os == 'Windows':
            platforms={'x86': 'Win32', 'x86_64': 'x64'}
            output_rpath = os.path.join(platforms.get(str(self.settings.arch)), str(self.settings.build_type))
            if self.options.shared:   
                self.copy("wavpackdll.*", dst=os.path.join(self.package_folder,"lib"),
                          src=os.path.join(self.build_folder,self._source_subfolder,output_rpath), excludes="wavpackdll.dll")
                self.copy("wavpackdll.dll", dst=os.path.join(self.package_folder,"bin"),
                          src=os.path.join(self.build_folder,self._source_subfolder,output_rpath))
            else:
                self.copy("libwavpack.*", dst=os.path.join(self.package_folder,"lib"),
                          src=os.path.join(self.build_folder,self._source_subfolder,output_rpath))

            tools.mkdir(os.path.join(self.package_folder,"lib","pkgconfig"))
            shutil.copyfile(os.path.join(self.build_folder,self._source_subfolder,"wavpack.pc.in"),
                            os.path.join(self.package_folder,"lib","pkgconfig", "wavpack.pc"))
            replacements = {
                "@prefix@"          : self.package_folder,
                "@exec_prefix@"     : "${prefix}/bin",
                "@libdir@"          : "${prefix}/lib",
                "@includedir@"      : "${prefix}/include",
                "@PACKAGE_VERSION@" : self.version,
                "@LIBM@"            : ""
            }
            for s, r in replacements.items():
                tools.replace_in_file(os.path.join(self.package_folder,"lib","pkgconfig", "wavpack.pc"),s,r)

        #if tools.os_info.is_linux:
        #    with tools.chdir(self.source_subfolder):
        #        self.copy("*", src="%s/builddir"%(os.getcwd()))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

