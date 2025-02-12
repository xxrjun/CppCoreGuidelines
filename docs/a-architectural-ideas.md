# A: Architectural ideas {#S-A}

This section contains ideas about higher-level architectural ideas and libraries.

Architectural rule summary:

* [A.1: Separate stable code from less stable code](#Ra-stable)
* [A.2: Express potentially reusable parts as a library](#Ra-lib)
* [A.4: There should be no cycles among libraries](#Ra-dag)
* [???](#???)
* [???](#???)
* [???](#???)
* [???](#???)
* [???](#???)
* [???](#???)

### <a name="Ra-stable"></a>A.1: Separate stable code from less stable code

Isolating less stable code facilitates its unit testing, interface improvement, refactoring, and eventual deprecation.

### <a name="Ra-lib"></a>A.2: Express potentially reusable parts as a library

##### Reason

##### Note

A library is a collection of declarations and definitions maintained, documented, and shipped together.
A library could be a set of headers (a "header-only library") or a set of headers plus a set of object files.
You can statically or dynamically link a library into a program, or you can `#include` a header-only library.


### <a name="Ra-dag"></a>A.4: There should be no cycles among libraries

##### Reason

* A cycle complicates the build process.
* Cycles are hard to understand and might introduce indeterminism (unspecified behavior).

##### Note

A library can contain cyclic references in the definition of its components.
For example:

    ???

However, a library should not depend on another that depends on it.
