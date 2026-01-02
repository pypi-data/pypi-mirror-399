#! /usr/bin/env python3


import os, sys, re
import yaml

loaded = dict()

try:
    import _ctemplate
    loaded['ctemplate'] = True
except:
    loaded['ctemplate'] = False

try:
    import mako.template
    loaded['mako'] = True
except:
    loaded['mako'] = False

try:
    import jinja2
    loaded['jinja'] = True
except:
    loaded['jinja'] = False

try:
    import tempita
    loaded['Tempita'] = True
except:
    loaded['Tempita'] = False

try:
    import pyratemp
    loaded['pyratemp'] = True
except:
    loaded['pyratemp'] = False

try:
    import wheezy.template.engine
    import wheezy.template.ext.core
    import wheezy.template.loader
    loaded['wheezy'] = True
except:
    loaded['wheezy'] = False



from argparse import ArgumentParser

def main():
    parser = ArgumentParser(description="A small utility to render template files. Rendering can be performed based on data stored in a YAML configuration file.")
    parser.add_argument("templateFiles",
                        action="store",
                        nargs='*',
                        help="Template files to be rendered.")
    parser.add_argument("-c", "--context",
                        action="store",
                        dest="contextFile",
                        help="YAML file containing template context.")
    parser.add_argument("-C", "--config",
                        action="store",
                        dest="configFiles",
                        nargs='*',
                        default=[],
                        help="YAML configuration files.")
    parser.add_argument("-o", "--output",
                        action="store",
                        dest="outputFile",
                        default="/dev/stdout",
                        help="Send rendered output to OUTPUTFILE.")

    parser.add_argument("-x", "--overwrite",    action="store_true", dest='overwrite', default=False,            help="Overwrite output files.")
    parser.add_argument("-n", "--no-overwrite", action="store_false",dest='overwrite', default=True,             help="Do not overwrite output files.")
    parser.add_argument("-a", "--auto-output",  action="store_true",                   default=False,            help="Automatically name output file.")
    parser.add_argument("-e", "--engine",       action="store",                        default="jinja",           help="The template engine to use.")
    parser.add_argument("-l", "--list",         action="store_true",                   default=False,            help="List available engines.")

    args = parser.parse_args()

    def renderTemplate(templateFile,data,outputFile):
      '''Renders a template from a templateFile with data to an outputFile'''
      # read template file into a string. some engines requires this.
      if not os.path.isfile( templateFile ):
          raise IOError( "file '"+templateFile+"' does not exist")
      templateText = ""
      with open( templateFile ) as f:
          templateText = f.read()

      # make sure we are not going to overwrite template file
      if outputFile == templateFile:
          raise IOError( "Output file (%s) would overwrite template file (%s)" % (outputFile,templateFile) )

      # check if we are going to overwrite existing file
      if outputFile != '/dev/stdout' and not args.overwrite and os.path.isfile( outputFile ):
        print("output file '"+outputFile+"' exists, please delete, move, or rerun with --overwrite option")
        sys.exit(1)

      # render
      with open( outputFile, "w" ) as f:

        if args.engine == 'ctemplate':
            f.write( _ctemplate.compile_template( templateText, data ) )

        if args.engine == 'mako':
          t = mako.template.Template(filename=templateFile)
          f.write( t.render( **data ) )

        if args.engine == 'jinja':
          t = jinja2.Template(templateText)
          f.write( t.render( **data ) )

        if args.engine == 'Tempita':
          t = tempita.Template(templateText)
          f.write( t.substitute( **data ) )

    # determine the output filename
    # using a function here so we can just return as soon as we find one that works
    def getOutputFile( config ):
      if args.outputFile == "/dev/stdout" and args.auto_output:
        # look for a filename in the config
        outputFile = config.get("output_file", None)
        if outputFile is not None:
            return outputFile

        # try to remove ".template" from the template filename
        outputFile = re.sub( "\.template$", "", templateFile )
        if outputFile != templateFile:
            return outputFile

      return args.outputFile



    if args.list:
      fmt = "{:>10} {:<20}"
      print(fmt.format("engine", "available?"))
      print("="*25)
      default_engine = parser.get_default('engine')
      for key in loaded:
        is_default = " (default)" if key == default_engine else ""
        print(fmt.format(key, "yes" if loaded[key] else "no" ) + is_default)
      sys.exit(0)



    # check that the engine is supported
    if not args.engine in loaded:
        print("'"+args.engine + "' engine is not recognized. Did you spell it correctly?")
        sys.exit(1)

    # check that the engine loaded
    if not loaded[args.engine]:
        print("'"+args.engine + "' engine did not load. Make sure that it is installed and available?")
        sys.exit(1)



    # generate configurations for command line arguments
    configs = []
    for templateFile in args.templateFiles:
      configs.append( {'template_file' : templateFile} )
      if args.contextFile:
        if not os.path.isfile( args.contextFile ):
          raise IOError( "file '"+args.contextFile+"' does not exist")
        with open( args.contextFile ) as f:
          data = yaml.safe_load(f)
          configs[-1]['data'] = data


    # read config files
    for configFile in args.configFiles:
      if os.path.isfile( configFile ):
          with open( configFile ) as f:
            # each YAML config file may contain multiple documents
            configGenerator = yaml.safe_load_all(f)
            configs += [ config for config in configGenerator ]
      else:
          raise IOError( "file '"+configFile+"' does not exist")





    for config in configs:

      # get template file
      templateFile = config.get( "template_file", "default.template" )
      # get the data that will be rendered
      data = config.get("data",{})
      # get output filename
      outputFile = getOutputFile(config)

      # render
      renderTemplate( templateFile, data, outputFile )

if __name__ == "__main__":
    main()

            



