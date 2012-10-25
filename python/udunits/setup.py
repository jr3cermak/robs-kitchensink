from distutils.core import setup, Extension

# Note: Change the directory locations below so it can
#       find your udunits library and include files
##

setup(name = "Udunits",
  version = "1.0",
  ext_modules = [Extension("udunits",
    ["udunits.c"], 
    include_dirs=['/usr/local/udunits/include'], 
    libraries = ["udunits2"], 
    library_dirs=['/usr/local/udunits/lib'])
    ]
  )
