from django import template


class Library(template.Library):
    def empty_tag(self, takes_context=None, name=None):
        def decorator(func):
            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
                return ''
            return self.simple_tag(wrapper, takes_context=takes_context, name=name)
        return decorator

    # def block_tag(self, node_class, name=None):
    #     def decorator(func):
    #         def wrapper(parser, token):
    #             if func.__name__[:3] != 'do_':
    #                 raise NameError
    #             name_ = func.__name__[3:] if name is None else name

    def raise_block_tag_with_as_error(self, name):
        raise template.TemplateSyntaxError("Invalid syntax for '{name}'. Use {open} {name} {close} or {open} {name} "
                                           "as variable {close}".format(name=name, open='{%', close='%}'))


class Node(template.Node):
    pass
