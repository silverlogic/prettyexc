
from .environment import default_unicode_environment, default_repr_environment

def _arg_to_unicode(arg, env):
    if isinstance(arg, unicode):
        return u''.join((env.STR_QUOTE, arg, env.STR_QUOTE))
    elif isinstance(arg, str):
        return u''.join((env.STR_QUOTE, arg.decode(env.DEFAULT_CHARSET), env.STR_QUOTE))
    return unicode(arg)

def _kwarg_to_unicode(kw, arg, env):
    return u''.join((unicode(kw), u'=', _arg_to_unicode(arg, env)))


class PrettyException(Exception):
    message_format = None
    unicode_environment = default_unicode_environment
    repr_environment = default_repr_environment

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
   
    def _show_module(self):
        """Override to modify 'auto' behavior.""" 
        return self.__class__.__module__[:2] != '__'

    def _type(self, env):
        """Override to modify type expresson."""
        s = self.__class__.__name__
        mod = self.__class__.__module__
        show_module = env.SHOW_MODULE if env.SHOW_MODULE is not None else self._show_module()
        if show_module:
            s = '.'.join((mod, s))
        return s

    def _show_args(self, argss):
        """Override to modify 'auto' behavior."""
        return len(argss) > 0

    def _args(self, env):
        """Override to modify arguments expression."""
        if env.SHOW_ARGS is False:
            return ''
        if env.SHOW_ARGS is None and len(self.args) == 1 and not self.kwargs:
            return ''
        argss = [_arg_to_unicode(arg, env) for arg in self.args]
        argss += [_kwarg_to_unicode(kw, arg, env) for kw, arg in self.kwargs.items()]
        if env.SHOW_ARGS is not True and not self._show_args(argss):
            return ''
        return u','.join(argss)
  
    def _show_message(self, msg):
        """Override to modify 'auto' behavior."""
        return msg

    def _message(self, env):
        """Override to modify message expression."""
        if env.SHOW_MESSAGE == False:
            return ''
        msg = self.message
        if not self._show_message(msg):
            return ''
        return msg

    def format(self, env):
        """Top-level formatter. Override other methods to keep total form."""
        ss = []
        if env.SHOW_CHEVRONS:
            ss.append(u'<')
        ss.append(self._type(env))
        args = self._args(env)
        if args:
            ss.append(u'(')
            ss.append(args)
            ss.append(u')')
        msg = self._message(env)
        if msg:
            ss.append(u': ')
            ss.append(msg)
        if env.SHOW_CHEVRONS:
            ss.append(u'>')
        return u''.join(ss)

    def __repr__(self):
        return self.format(self.repr_environment)

    def __unicode__(self):
        return self.format(self.unicode_environment)

    def __str__(self):
        return self.__unicode__().encode(self.unicode_environment.DEFAULT_CHARSET)

    @property
    def message(self):
        """Default message builder from message_format."""
        fmt = self.message_format
        if not fmt:
            if len(self.args) == 1 and not self.kwargs:
                return unicode(self.args[0]) # Python default Exception behavior
            return ''
        return fmt.format(*self.args, **self.kwargs)
