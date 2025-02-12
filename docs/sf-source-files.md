# SF: Source files {#S-source}

Distinguish between declarations (used as interfaces) and definitions (used as implementations).
Use header files to represent interfaces and to emphasize logical structure.

Source file rule summary:

* [SF.1: Use a `.cpp` suffix for code files and `.h` for interface files if your project doesn't already follow another convention](#Rs-file-suffix)
* [SF.2: A header file must not contain object definitions or non-inline function definitions](#Rs-inline)
* [SF.3: Use header files for all declarations used in multiple source files](#Rs-declaration-header)
* [SF.4: Include header files before other declarations in a file](#Rs-include-order)
* [SF.5: A `.cpp` file must include the header file(s) that defines its interface](#Rs-consistency)
* [SF.6: Use `using namespace` directives for transition, for foundation libraries (such as `std`), or within a local scope (only)](#Rs-using)
* [SF.7: Don't write `using namespace` at global scope in a header file](#Rs-using-directive)
* [SF.8: Use `#include` guards for all header files](#Rs-guards)
* [SF.9: Avoid cyclic dependencies among source files](#Rs-cycles)
* [SF.10: Avoid dependencies on implicitly `#include`d names](#Rs-implicit)
* [SF.11: Header files should be self-contained](#Rs-contained)
* [SF.12: Prefer the quoted form of `#include` for files relative to the including file and the angle bracket form everywhere else](#Rs-incform)
* [SF.13: Use portable header identifiers in `#include` statements](#Rs-portable-header-id)

* [SF.20: Use `namespace`s to express logical structure](#Rs-namespace)
* [SF.21: Don't use an unnamed (anonymous) namespace in a header](#Rs-unnamed)
* [SF.22: Use an unnamed (anonymous) namespace for all internal/non-exported entities](#Rs-unnamed2)

### <a name="Rs-file-suffix"></a>SF.1: Use a `.cpp` suffix for code files and `.h` for interface files if your project doesn't already follow another convention

See [NL.27](#Rl-file-suffix)

### <a name="Rs-inline"></a>SF.2: A header file must not contain object definitions or non-inline function definitions

##### Reason

Including entities subject to the one-definition rule leads to linkage errors.

##### Example

    // file.h:
    namespace Foo {
        int x = 7;
        int xx() { return x+x; }
    }

    // file1.cpp:
    #include <file.h>
    // ... more ...

     // file2.cpp:
    #include <file.h>
    // ... more ...

Linking `file1.cpp` and `file2.cpp` will give two linker errors.

**Alternative formulation**: A header file must contain only:

* `#include`s of other header files (possibly with include guards)
* templates
* class definitions
* function declarations
* `extern` declarations
* `inline` function definitions
* `constexpr` definitions
* `const` definitions
* `using` alias definitions
* ???

##### Enforcement

Check the positive list above.

### <a name="Rs-declaration-header"></a>SF.3: Use header files for all declarations used in multiple source files

##### Reason

Maintainability. Readability.

##### Example, bad

    // bar.cpp:
    void bar() { cout << "bar\n"; }

    // foo.cpp:
    extern void bar();
    void foo() { bar(); }

A maintainer of `bar` cannot find all declarations of `bar` if its type needs changing.
The user of `bar` cannot know if the interface used is complete and correct. At best, error messages come (late) from the linker.

##### Enforcement

* Flag declarations of entities in other source files not placed in a `.h`.

### <a name="Rs-include-order"></a>SF.4: Include header files before other declarations in a file

##### Reason

Minimize context dependencies and increase readability.

##### Example

    #include <vector>
    #include <algorithm>
    #include <string>

    // ... my code here ...

##### Example, bad

    #include <vector>

    // ... my code here ...

    #include <algorithm>
    #include <string>

##### Note

This applies to both `.h` and `.cpp` files.

##### Note

There is an argument for insulating code from declarations and macros in header files by `#including` headers *after* the code we want to protect
(as in the example labeled "bad").
However

* that only works for one file (at one level): Use that technique in a header included with other headers and the vulnerability reappears.
* a namespace (an "implementation namespace") can protect against many context dependencies.
* full protection and flexibility require modules.

**See also**:

* [Working Draft, Extensions to C++ for Modules](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/n4592.pdf)
* [Modules, Componentization, and Transition](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0141r0.pdf)

##### Enforcement

Easy.

### <a name="Rs-consistency"></a>SF.5: A `.cpp` file must include the header file(s) that defines its interface

##### Reason

This enables the compiler to do an early consistency check.

##### Example, bad

    // foo.h:
    void foo(int);
    int bar(long);
    int foobar(int);

    // foo.cpp:
    void foo(int) { /* ... */ }
    int bar(double) { /* ... */ }
    double foobar(int);

The errors will not be caught until link time for a program calling `bar` or `foobar`.

##### Example

    // foo.h:
    void foo(int);
    int bar(long);
    int foobar(int);

    // foo.cpp:
    #include "foo.h"

    void foo(int) { /* ... */ }
    int bar(double) { /* ... */ }
    double foobar(int);   // error: wrong return type

The return-type error for `foobar` is now caught immediately when `foo.cpp` is compiled.
The argument-type error for `bar` cannot be caught until link time because of the possibility of overloading, but systematic use of `.h` files increases the likelihood that it is caught earlier by the programmer.

##### Enforcement

???

### <a name="Rs-using"></a>SF.6: Use `using namespace` directives for transition, for foundation libraries (such as `std`), or within a local scope (only)

##### Reason

 `using namespace` can lead to name clashes, so it should be used sparingly.
 However, it is not always possible to qualify every name from a namespace in user code (e.g., during transition)
 and sometimes a namespace is so fundamental and prevalent in a code base, that consistent qualification would be verbose and distracting.

##### Example

    #include <string>
    #include <vector>
    #include <iostream>
    #include <memory>
    #include <algorithm>

    using namespace std;

    // ...

Here (obviously), the standard library is used pervasively and apparently no other library is used, so requiring `std::` everywhere
could be distracting.

##### Example

The use of `using namespace std;` leaves the programmer open to a name clash with a name from the standard library

    #include <cmath>
    using namespace std;

    int g(int x)
    {
        int sqrt = 7;
        // ...
        return sqrt(x); // error
    }

However, this is not particularly likely to lead to a resolution that is not an error and
people who use `using namespace std` are supposed to know about `std` and about this risk.

##### Note

A `.cpp` file is a form of local scope.
There is little difference in the opportunities for name clashes in an N-line `.cpp` containing a `using namespace X`,
an N-line function containing a `using namespace X`,
and M functions each containing a `using namespace X`with N lines of code in total.

##### Note

[Don't write `using namespace` at global scope in a header file](#Rs-using-directive).

### <a name="Rs-using-directive"></a>SF.7: Don't write `using namespace` at global scope in a header file

##### Reason

Doing so takes away an `#include`r's ability to effectively disambiguate and to use alternatives. It also makes `#include`d headers order-dependent as they might have different meaning when included in different orders.

##### Example

    // bad.h
    #include <iostream>
    using namespace std; // bad

    // user.cpp
    #include "bad.h"

    bool copy(/*... some parameters ...*/);    // some function that happens to be named copy

    int main()
    {
        copy(/*...*/);    // now overloads local ::copy and std::copy, could be ambiguous
    }

##### Note

An exception is `using namespace std::literals;`. This is necessary to use string literals
in header files and given [the rules](http://eel.is/c++draft/over.literal) - users are required
to name their own UDLs `operator""_x` - they will not collide with the standard library.

##### Enforcement

Flag `using namespace` at global scope in a header file.

### <a name="Rs-guards"></a>SF.8: Use `#include` guards for all header files

##### Reason

To avoid files being `#include`d several times.

In order to avoid include guard collisions, do not just name the guard after the filename.
Be sure to also include a key and good differentiator, such as the name of library or component
the header file is part of.

##### Example

    // file foobar.h:
    #ifndef LIBRARY_FOOBAR_H
    #define LIBRARY_FOOBAR_H
    // ... declarations ...
    #endif // LIBRARY_FOOBAR_H

##### Enforcement

Flag `.h` files without `#include` guards.

##### Note

Some implementations offer vendor extensions like `#pragma once` as alternative to include guards.
It is not standard and it is not portable.  It injects the hosting machine's filesystem semantics
into your program, in addition to locking you down to a vendor.
Our recommendation is to write in ISO C++: See [rule P.2](#Rp-Cplusplus).

### <a name="Rs-cycles"></a>SF.9: Avoid cyclic dependencies among source files

##### Reason

Cycles complicate comprehension and slow down compilation. They also
complicate conversion to use language-supported modules (when they become
available).

##### Note

Eliminate cycles; don't just break them with `#include` guards.

##### Example, bad

    // file1.h:
    #include "file2.h"

    // file2.h:
    #include "file3.h"

    // file3.h:
    #include "file1.h"

##### Enforcement

Flag all cycles.


### <a name="Rs-implicit"></a>SF.10: Avoid dependencies on implicitly `#include`d names

##### Reason

Avoid surprises.
Avoid having to change `#include`s if an `#include`d header changes.
Avoid accidentally becoming dependent on implementation details and logically separate entities included in a header.

##### Example, bad

    #include <iostream>
    using namespace std;

    void use()
    {
        string s;
        cin >> s;               // fine
        getline(cin, s);        // error: getline() not defined
        if (s == "surprise") {  // error == not defined
            // ...
        }
    }

`<iostream>` exposes the definition of `std::string` ("why?" makes for a fun trivia question),
but it is not required to do so by transitively including the entire `<string>` header,
resulting in the popular beginner question "why doesn't `getline(cin,s);` work?"
or even an occasional "`string`s cannot be compared with `==`").

The solution is to explicitly `#include <string>`:

##### Example, good

    #include <iostream>
    #include <string>
    using namespace std;

    void use()
    {
        string s;
        cin >> s;               // fine
        getline(cin, s);        // fine
        if (s == "surprise") {  // fine
            // ...
        }
    }

##### Note

Some headers exist exactly to collect a set of consistent declarations from a variety of headers.
For example:

    // basic_std_lib.h:

    #include <string>
    #include <map>
    #include <iostream>
    #include <random>
    #include <vector>

a user can now get that set of declarations with a single `#include`

    #include "basic_std_lib.h"

This rule against implicit inclusion is not meant to prevent such deliberate aggregation.

##### Enforcement

Enforcement would require some knowledge about what in a header is meant to be "exported" to users and what is there to enable implementation.
No really good solution is possible until we have modules.

### <a name="Rs-contained"></a>SF.11: Header files should be self-contained

##### Reason

Usability, headers should be simple to use and work when included on their own.
Headers should encapsulate the functionality they provide.
Avoid clients of a header having to manage that header's dependencies.

##### Example

    #include "helpers.h"
    // helpers.h depends on std::string and includes <string>

##### Note

Failing to follow this results in difficult to diagnose errors for clients of a header.

##### Note

A header should include all its dependencies. Be careful about using relative paths because C++ implementations diverge on their meaning.

##### Enforcement

A test should verify that the header file itself compiles or that a cpp file which only includes the header file compiles.

### <a name="Rs-incform"></a>SF.12: Prefer the quoted form of `#include` for files relative to the including file and the angle bracket form everywhere else

##### Reason

The [standard](http://eel.is/c++draft/cpp.include) provides flexibility for compilers to implement
the two forms of `#include` selected using the angle (`<>`) or quoted (`""`) syntax. Vendors take
advantage of this and use different search algorithms and methods for specifying the include path.

Nevertheless, the guidance is to use the quoted form for including files that exist at a relative path to the file containing the `#include` statement (from within the same component or project) and to use the angle bracket form everywhere else, where possible. This encourages being clear about the locality of the file relative to files that include it, or scenarios where the different search algorithm is required. It makes it easy to understand at a glance whether a header is being included from a local relative file versus a standard library header or a header from the alternate search path (e.g. a header from another library or a common set of includes).

##### Example

    // foo.cpp:
    #include <string>                // From the standard library, requires the <> form
    #include <some_library/common.h> // A file that is not locally relative, included from another library; use the <> form
    #include "foo.h"                 // A file locally relative to foo.cpp in the same project, use the "" form
    #include "util/util.h"           // A file locally relative to foo.cpp in the same project, use the "" form
    #include <component_b/bar.h>     // A file in the same project located via a search path, use the <> form

##### Note

Failing to follow this results in difficult to diagnose errors due to picking up the wrong file by incorrectly specifying the scope when it is included. For example, in a typical case where the `#include ""` search algorithm might search for a file existing at a local relative path first, then using this form to refer to a file that is not locally relative could mean that if a file ever comes into existence at the local relative path (e.g. the including file is moved to a new location), it will now be found ahead of the previous include file and the set of includes will have been changed in an unexpected way.

Library creators should put their headers in a folder and have clients include those files using the relative path `#include <some_library/common.h>`

##### Enforcement

A test should identify whether headers referenced via `""` could be referenced with `<>`.

### <a name="Rs-portable-header-id"></a>SF.13: Use portable header identifiers in `#include` statements

##### Reason

The [standard](http://eel.is/c++draft/cpp.include) does not specify how compilers uniquely locate headers from an identifier in an `#include` directive, nor does it specify what constitutes uniqueness. For example, whether the implementation considers the identifiers to be case-sensitive, or whether the identifiers are file system paths to a header file, and if so, how a hierarchical file system path is delimited.

To maximize the portability of `#include` directives across compilers, guidance is to:

* use case-sensitivity for the header identifier, matching how the header is defined by the standard, specification, implementation, or file that provides the header.
* when the header identifier is a hierarchical file path, use forward-slash `/` to delimit path components as this is the most widely-accepted path-delimiting character.

##### Example

    // good examples
    #include <vector>
    #include <string>
    #include "util/util.h"

    // bad examples
    #include <VECTOR>        // bad: the standard library defines a header identified as <vector>, not <VECTOR>
    #include <String>        // bad: the standard library defines a header identified as <string>, not <String>
    #include "Util/Util.H"   // bad: the header file exists on the file system as "util/util.h"
    #include "util\util.h"   // bad: may not work if the implementation interprets `\u` as an escape sequence, or where '\' is not a valid path separator

##### Enforcement

It is only possible to enforce on implementations where header identifiers are case-sensitive and which only support `/` as a file path delimiter.

### <a name="Rs-namespace"></a>SF.20: Use `namespace`s to express logical structure

##### Reason

 ???

##### Example

    ???

##### Enforcement

???

### <a name="Rs-unnamed"></a>SF.21: Don't use an unnamed (anonymous) namespace in a header

##### Reason

It is almost always a bug to mention an unnamed namespace in a header file.

##### Example

    // file foo.h:
    namespace
    {
        const double x = 1.234;  // bad

        double foo(double y)     // bad
        {
            return y + x;
        }
    }

    namespace Foo
    {
        const double x = 1.234; // good

        inline double foo(double y)        // good
        {
            return y + x;
        }
    }

##### Enforcement

* Flag any use of an anonymous namespace in a header file.

### <a name="Rs-unnamed2"></a>SF.22: Use an unnamed (anonymous) namespace for all internal/non-exported entities

##### Reason

Nothing external can depend on an entity in a nested unnamed namespace.
Consider putting every definition in an implementation source file in an unnamed namespace unless that is defining an "external/exported" entity.

##### Example; bad

    static int f();
    int g();
    static bool h();
    int k();

##### Example; good

    namespace {
        int f();
        bool h();
    }
    int g();
    int k();

##### Example

An API class and its members can't live in an unnamed namespace; but any "helper" class or function that is defined in an implementation source file should be at an unnamed namespace scope.

    ???

##### Enforcement

* ???
