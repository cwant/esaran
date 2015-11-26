# eSaran Callback Wrappers #

The main work horse of the wrappers is the function `eSaran.do_wrapper()` and this is the function that you pass your callback functions to.

## `eSaran.do_wrapper()` ##

The usage of this function is as follows:

```
     eSaran.do_wrapper(get_wrapper_cmdline,
                       wrapper_title,
                       add_wrapper_options,
                       wrapper_gui_options,
                       configfileXML)
```

A description of the arguments is as follows:

### `get_wrapper_cmdline(config, options)` ###

This callback function takes the two dictionaries `config` and `options` and returns a string that will be executed during the job. For example, suppose we are writing a wrapper for a program called `cure_cancer` and that this wrapper has two command line options `-L`/`--level` and `-T`/`--time` (adding command line arguments will be discussed later in this document). Suppose the values for these arguments are stored in the `options` dict as `options["level"]` and `options["time"]`. Then a reasonable callback for function for `get_wrapper_cmdline()` might be:

```
def get_wrapper_cmdline(config, options):
    return "cure_cancer -L %s -T %s" % (options["level"], options["time"])
```

The returned string can be multi-line if needed, allowing for such things as setting up of options and post processing output. For example,:

```
def get_wrapper_cmdline(config, options):
    return """ \
export PATH=/usr/local/cure_cancer-1.2.7
cure_cancer -L %(level)s -T %{time)s > data.out
cat data.out | nl > numdata
""" % (options)
```

### `wrapper_title` ###

This is a string that contains the name of the wrapper, in plain English. This is used in the help/usage text (`-h`/`--help`) and in the optional GUI. For our example above, we might have `wrapper_title="Wrap cure_cancer"`.

### `add_wrapper_options(parser, config)` ###

This callback function lets you add command line options to your wrapper. The input to the wrapper is an `optparse` `parser`, and the `config` dict. An example callback using our recurring example might be:

```
def add_wrapper_options(parser, config):
    import eSaran, optparse 

    g = optparse.OptionGroup(parser, "Options for cure_cancer")

    ### Level
    g.add_option("-L", "--level", action="callback",
                 callback=eSaran.store_seen, type="string",
                 dest="level", metavar="DOSAGE",
                 help="The dosage required, in millilitres")

    ### Time
    g.add_option("-T", "--time", action="callback",
                 callback=eSaran.store_seen, type="string",
                 dest="time", metavar="SECONDS",
                 default="20s",
                 help="The recovery period, in seconds (default: %default)")

    parser.add_option_group(g)
```

### `wrapper_gui_options(subpanel, config, options)` ###

This callback can add options to the wxPython GUI for the wrapper. The first argument is a wxPython Panel object that holds the `subpanel` into which the custom GUI controls will be added. The second argument is the `config` dict for the wrapper. The third option is the `options` dict for the wrapper. This function must return a tuple. The first member of the tuple is the title (a strung) for the `subpanel`. The second member of the tuple is a list describing the controls in the subpanel. Each member of this list is itself a list of two items: the first item is the name of the control, the second is a wxPython `Ctrl`. The utility functions `eSaran.add_text_control()`, `eSaran.add_combo_control()`, `eSaran.add_spin_control()`, and `eSaran.add_checkbox_control()` can be used to help create these controls.

An implementation of `wrapper_gui_options()` for our example could be:

```
def wrapper_gui_options(subpanel, config, options):
    import eSaran
    title = "cure_cancer options"
    fields = []
    fields.append(eSaran.add_text_control(subpanel,
                                          "level",
                                          "Dosage level:",
                                          width=30))
    fields.append(eSaran.add_text_control(subpanel,
                                          "time",
                                          "Recovery time in seconds:",
                                          width=30))

    return (title, fields)
```

### `configfileXML` ###

This is a string containing a XML description of the wrapper functionality. The default value for this is an empty string. If the value of this string is non-empty, the other callbacks will be ignored and the XML description will be used instead. See the section on the [XML method](eSaranXMLwrappers.md) for more details. An example XML file describing our example application might look like:

```
<wrapper>

  <wrapper_title>Wrap cure_cancer</wrapper_title>
  <options_title>cure_cancer Options</options_title>

  <arguments>
    <argument>
       <name>level</name>
       <short>-L</short>
       <long>--level</long>
          <gui_title>Dosage level:</gui_title>
          <help>The dosage in millilitres</help>
        </argument>

        <argument>
          <name>time</name>
          <short>-T</short>
          <long>--time</long>
          <gui_title>Recovery time in seconds:</gui_title>
          <help>The recovery period, in seconds (default: %default)</help>
        </argument>
  </arguments>

  <hosts>
    <host type="defaults">
      <command>
cure_cancer -L %(level) -T %(time)
      </command>
    </host>

    <host>
      <name>cluster.srv.ualberta.ca</name>
      <command>
export PATH=/usr/local/cure_cancer-10.5.1
cure_cancer -L %(level) -T %(time)
      </command>
    </host>

  </hosts>
</wrapper>
```