import config

if config.PREFER_Z3C_PT:
    from z3c.pt.pagetemplate import ViewPageTemplateFile

    def bind_template(pt, view):
        return pt.bind(view)    
else:
    from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile    
    from zope.app.pagetemplate.viewpagetemplatefile import BoundPageTemplate as \
         bind_template
    
class ViewPageTemplateFile(ViewPageTemplateFile):
    pass
