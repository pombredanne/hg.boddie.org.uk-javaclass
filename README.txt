Investigate better exception raising. Currently, exceptions have to be
derived from object so that object.__new__ can be used upon them. However,
this seems to prevent them from being raised, and they need to be wrapped
within Exception so that the information can be transmitted to the
exception's handler.

Consider nicer ways of writing the method names in Python, perhaps using a
function which takes the individual parameter types as arguments.
