===================
ObjectWidget caveat
===================

ObjectWidget itself seems to be fine, but we discovered a fundamental problem
in z3c.form.

The meat is that widget value
* validation
* extraction
* applying values
need to be separated and made recursive-aware.

Currently
---------
* There is a loop that extracts and validates each widgets value.
  Then it moves on to the next widget in the same loop.
* The problem is that the ObjectWidget MUST keep it's values in the object itself,
  not in any dict or helper structure.
  That means in case of a validation failure later in the loop the ObjectWidget's
  values are already applied and cannot be reverted.
* Also on a single level of widgets this loop might be OK,
  because the loop is just flat.

We need
-------
* To do a loop to validate ALL widget values.
* To do a loop to extract ALL values. (maybe apply too, let's think about it...)
* Then in a different loop apply those extracted (and validated) values.
* Problem is that the current API does not support separate methods for that.
* One more point is to take into account that with the ObjectWidget forms and
  widgets can be _recursive_, that means there can be a
  form-widgets-subform-widgets-subform-widgets level of widgets.


An example:

> The situation is the following:
> - schema is like this:
> class IMySubObject(zope.interface.Interface):
>     foofield = zope.schema.Int(
>         title=u"My foo field",
>         default=1111,
>         max=9999)
>     barfield = zope.schema.Int(
>         title=u"My dear bar",
>         default=2222,
>         required=False)
> class IMyObject(zope.interface.Interface):
>     subobject = zope.schema.Object(title=u'my object',
>                                    schema=IMySubObject)
>     name = zope.schema.TextLine(title=u'name')
>
> - on object editing
> - we need to keep the (**old**) (IMySubObject) object in place
>   -- do not create a new one
> - value setting is done in the editform handleApply
>   - extractData, extract needs to extract recursively
>   - return assignable values
>   - it has no idea about subobjects
> - let's say the IMySubObject data is validated OK, but there's an
>   error in IMyObject (with name)
> - now the problem is:
>   - IMyObject.subobject extract gets called first
>     it sets the values on the existing object (and fires
>     ObjectModifiedEvent)
>   - IMyObject.name detects the error
>     it does not set the value
>   BUT IMyObject.subobject sticks to the extracted value that should be
>   discarded, because the whole form did not validate?!?!?!
