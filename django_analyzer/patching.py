from functools import partial, wraps
from django_analyzer.contextmanager import context, measure


def patch(target, method_name):
    @wraps
    def wrap(func):
        target_method = getattr(target, method_name, None)
        patched_method_name = '_patched_' + method_name
        patched_target_method = getattr(target, patched_method_name, None)
        if patched_target_method is None:
            if target_method is None:
                def placeholder(*args, **kwargs):
                    return None
                target_method = placeholder
            setattr(target, patched_method_name, target_method)
            setattr(target, method_name, func)
        return partial(func, target_method)

    return wrap


def patch_template_rendering():
    from django import shortcuts
    from django.shortcuts import render as django_render
    from django.shortcuts import render_to_response as django_render_to_response
    from django.template.loader_tags import BlockNode

    def analyze_render(request, *args, **kwargs):
        context.timeline.time_split('render')
        return django_render(request, *args, **kwargs)
    analyze_render.patched = True

    def analyze_render_to_response(*args, **kwargs):
        context.timeline.time_split('render')
        return django_render_to_response(*args, **kwargs)
    analyze_render_to_response.patched = True

    def analyze_block_render(self, context):
        with measure(('block', self.name)):
            result = BlockNode._render(self, context)
        return result
    analyze_block_render.patched = True

    if not getattr(shortcuts.render, 'patched', False):
        shortcuts.render = analyze_render
    if not getattr(shortcuts.render_to_response, 'patched', False):
        shortcuts.render_to_response = analyze_render_to_response
    if not getattr(BlockNode.render, 'patched', False):
        BlockNode._render = BlockNode.render
        BlockNode.render = analyze_block_render


def patch_middlewares():
    from django.conf import settings
    from django.utils.importlib import import_module

    def import_middleware(class_string):
        module, clazz = class_string.rsplit('.', 1)
        imported_module = import_module(module)
        return getattr(imported_module, clazz)

    middlewares = list(settings.MIDDLEWARE_CLASSES)
    toolbar_index = middlewares.index('debug_toolbar.middleware.DebugToolbarMiddleware')
    pre_middleware = import_middleware(middlewares[toolbar_index + 1])
    post_middleware = import_middleware(middlewares[-1])

    def pre_process_request(self, request):
        # print 'PATCHED PRE PROCESS REQEUEST'
        context.timeline.time_split(('middlewares', 'process_request'))
        return self._process_request(request) if self._process_request else None

    def pre_process_view(self, request, view_func, view_args, view_kwargs):
        # print 'PATCHED PRE PROCESS VIEW'
        context.timeline.time_split('view')
        context.profiler.start()
        ### Profile the view func
        # if self._process_view is None:
        #     return context.profiler.run(view_func, request, *view_args, **view_kwargs)
        # else:
        #     return context.profiler.run(self._process_view, request, view_func, view_args, view_kwargs)
        #
        return self._process_view(request, view_func, view_args, view_kwargs) if self._process_view else None

    def pre_process_response(self, request, response):
        # print 'PATCHED PRE PROCESS RESPONSE'
        context.timeline.time_split('end')
        context.profiler.stop()
        return self._process_response(request, response) if self._process_response else response

    def post_process_view(self, request, view_func, view_args, view_kwargs):
        # print 'PATCHED POST PROCESS VIEW'
        context.timeline.time_split('view')
        return self._process_view(request, view_func, view_args, view_kwargs) if self._process_view else None

    def post_process_template_response(self, request, response):
        # print 'PATCHED POST PROCESS TEMPLATE RESPONSE'
        context.timeline.time_split('render')
        return self._process_template_response(request, response) if self._process_template_response else response

    def post_process_response(self, request, response):
        # print 'PATCHED POST PROCESS RESPONSE'
        context.timeline.time_split('render', ('middlewares', 'process_response'))
        return self._process_response(request, response) if self._process_response else response

    def patch_middleware_method(middleware, method_name, patch):
        _method = getattr(middleware, method_name, None)
        if not _method or not getattr(_method, 'patched', False):
            setattr(middleware, '_' + method_name, _method)
            setattr(middleware, method_name, patch)
            patch.patched = True

    patch_middleware_method(pre_middleware, 'process_request', pre_process_request)
    patch_middleware_method(pre_middleware, 'process_view', pre_process_view)
    patch_middleware_method(pre_middleware, 'process_response', pre_process_response)
    patch_middleware_method(post_middleware, 'process_view', post_process_view)
    patch_middleware_method(post_middleware, 'process_template_response', post_process_template_response)
    patch_middleware_method(post_middleware, 'process_response', post_process_response)


def monkey_patch():
    patch_template_rendering()
    patch_middlewares()
