# NR: Non-Rules and myths {#S-not}

This section contains rules and guidelines that are popular somewhere, but that we deliberately don't recommend.
We know perfectly well that there have been times and places where these rules made sense, and we have used them ourselves at times.
However, in the context of the styles of programming we recommend and support with the guidelines, these "non-rules" would do harm.

Even today, there can be contexts where the rules make sense.
For example, lack of suitable tool support can make exceptions unsuitable in hard-real-time systems,
but please don't naïvely trust "common wisdom" (e.g., unsupported statements about "efficiency");
such "wisdom" might be based on decades-old information or experiences from languages with very different properties than C++
(e.g., C or Java).

The positive arguments for alternatives to these non-rules are listed in the rules offered as "Alternatives".

Non-rule summary:

* [NR.1: Don't insist that all declarations should be at the top of a function](#Rnr-top)
* [NR.2: Don't insist on having only a single `return`-statement in a function](#Rnr-single-return)
* [NR.3: Don't avoid exceptions](#Rnr-no-exceptions)
* [NR.4: Don't insist on placing each class definition in its own source file](#Rnr-lots-of-files)
* [NR.5: Don't use two-phase initialization](#Rnr-two-phase-init)
* [NR.6: Don't place all cleanup actions at the end of a function and `goto exit`](#Rnr-goto-exit)
* [NR.7: Don't make all data members `protected`](#Rnr-protected-data)
* ???

### <a name="Rnr-top"></a>NR.1: Don't insist that all declarations should be at the top of a function

##### Reason

The "all declarations on top" rule is a legacy of old programming languages that didn't allow initialization of variables and constants after a statement.
This leads to longer programs and more errors caused by uninitialized and wrongly initialized variables.

##### Example, bad

    int use(int x)
    {
        int i;
        char c;
        double d;

        // ... some stuff ...

        if (x < i) {
            // ...
            i = f(x, d);
        }
        if (i < x) {
            // ...
            i = g(x, c);
        }
        return i;
    }

The larger the distance between the uninitialized variable and its use, the larger the chance of a bug.
Fortunately, compilers catch many "used before set" errors.
Unfortunately, compilers cannot catch all such errors and unfortunately, the bugs aren't always as simple to spot as in this small example.


##### Alternative

* [Always initialize an object](#Res-always)
* [ES.21: Don't introduce a variable (or constant) before you need to use it](#Res-introduce)

### <a name="Rnr-single-return"></a>NR.2: Don't insist on having only a single `return`-statement in a function

##### Reason

The single-return rule can lead to unnecessarily convoluted code and the introduction of extra state variables.
In particular, the single-return rule makes it harder to concentrate error checking at the top of a function.

##### Example

    template<class T>
    //  requires Number<T>
    string sign(T x)
    {
        if (x < 0)
            return "negative";
        if (x > 0)
            return "positive";
        return "zero";
    }

to use a single return only we would have to do something like

    template<class T>
    //  requires Number<T>
    string sign(T x)        // bad
    {
        string res;
        if (x < 0)
            res = "negative";
        else if (x > 0)
            res = "positive";
        else
            res = "zero";
        return res;
    }

This is both longer and likely to be less efficient.
The larger and more complicated the function is, the more painful the workarounds get.
Of course many simple functions will naturally have just one `return` because of their simpler inherent logic.

##### Example

    int index(const char* p)
    {
        if (!p) return -1;  // error indicator: alternatively "throw nullptr_error{}"
        // ... do a lookup to find the index for p
        return i;
    }

If we applied the rule, we'd get something like

    int index2(const char* p)
    {
        int i;
        if (!p)
            i = -1;  // error indicator
        else {
            // ... do a lookup to find the index for p
        }
        return i;
    }

Note that we (deliberately) violated the rule against uninitialized variables because this style commonly leads to that.
Also, this style is a temptation to use the [goto exit](#Rnr-goto-exit) non-rule.

##### Alternative

* Keep functions short and simple
* Feel free to use multiple `return` statements (and to throw exceptions).

### <a name="Rnr-no-exceptions"></a>NR.3: Don't avoid exceptions

##### Reason

There seem to be four main reasons given for not using exceptions:

* exceptions are inefficient
* exceptions lead to leaks and errors
* exception performance is not predictable
* the exception-handling run-time support takes up too much space

There is no way we can settle this issue to the satisfaction of everybody.
After all, the discussions about exceptions have been going on for 40+ years.
Some languages cannot be used without exceptions, but others do not support them.
This leads to strong traditions for the use and non-use of exceptions, and to heated debates.

However, we can briefly outline why we consider exceptions the best alternative for general-purpose programming
and in the context of these guidelines.
Simple arguments for and against are often inconclusive.
There are specialized applications where exceptions indeed can be inappropriate
(e.g., hard-real-time systems without support for reliable estimates of the cost of handling an exception).

Consider the major objections to exceptions in turn

* Exceptions are inefficient:
Compared to what?
When comparing make sure that the same set of errors are handled and that they are handled equivalently.
In particular, do not compare a program that immediately terminates on seeing an error to a program
that carefully cleans up resources before logging an error.
Yes, some systems have poor exception handling implementations; sometimes, such implementations force us to use
other error-handling approaches, but that's not a fundamental problem with exceptions.
When using an efficiency argument - in any context - be careful that you have good data that actually provides
insight into the problem under discussion.
* Exceptions lead to leaks and errors.
They do not.
If your program is a rat's nest of pointers without an overall strategy for resource management,
you have a problem whatever you do.
If your system consists of a million lines of such code,
you probably will not be able to use exceptions,
but that's a problem with excessive and undisciplined pointer use, rather than with exceptions.
In our opinion, you need RAII to make exception-based error handling simple and safe -- simpler and safer than alternatives.
* Exception performance is not predictable.
If you are in a hard-real-time system where you must guarantee completion of a task in a given time,
you need tools to back up such guarantees.
As far as we know such tools are not available (at least not to most programmers).
* The exception-handling run-time support takes up too much space.
This can be the case in small (usually embedded) systems.
However, before abandoning exceptions consider what space consistent error-handling using error-codes would require
and what failure to catch an error would cost.

Many, possibly most, problems with exceptions stem from historical needs to interact with messy old code.

The fundamental arguments for the use of exceptions are

* They clearly differentiate between erroneous return and ordinary return
* They cannot be forgotten or ignored
* They can be used systematically

Remember

* Exceptions are for reporting errors (in C++; other languages can have different uses for exceptions).
* Exceptions are not for errors that can be handled locally.
* Don't try to catch every exception in every function (that's tedious, clumsy, and leads to slow code).
* Exceptions are not for errors that require instant termination of a module/system after a non-recoverable error.

##### Example

    ???

##### Alternative

* [RAII](#Re-raii)
* Contracts/assertions: Use GSL's `Expects` and `Ensures` (until we get language support for contracts)

### <a name="Rnr-lots-of-files"></a>NR.4: Don't insist on placing each class definition in its own source file

##### Reason

The resulting number of files from placing each class in its own file are hard to manage and can slow down compilation.
Individual classes are rarely a good logical unit of maintenance and distribution.

##### Example

    ???

##### Alternative

* Use namespaces containing logically cohesive sets of classes and functions.

### <a name="Rnr-two-phase-init"></a>NR.5: Don't use two-phase initialization

##### Reason

Splitting initialization into two leads to weaker invariants,
more complicated code (having to deal with semi-constructed objects),
and errors (when we didn't deal correctly with semi-constructed objects consistently).

##### Example, bad

    // Old conventional style: many problems

    class Picture
    {
        int mx;
        int my;
        int * data;
    public:
        // main problem: constructor does not fully construct
        Picture(int x, int y)
        {
            mx = x;         // also bad: assignment in constructor body
                            // rather than in member initializer
            my = y;
            data = nullptr; // also bad: constant initialization in constructor
                            // rather than in member initializer
        }

        ~Picture()
        {
            Cleanup();
        }

        // ...

        // bad: two-phase initialization
        bool Init()
        {
            // invariant checks
            if (mx <= 0 || my <= 0) {
                return false;
            }
            if (data) {
                return false;
            }
            data = (int*) malloc(mx*my*sizeof(int));   // also bad: owning raw * and malloc
            return data != nullptr;
        }

        // also bad: no reason to make cleanup a separate function
        void Cleanup()
        {
            if (data) free(data);
            data = nullptr;
        }
    };

    Picture picture(100, 0); // not ready-to-use picture here
    // this will fail..
    if (!picture.Init()) {
        puts("Error, invalid picture");
    }
    // now have an invalid picture object instance.

##### Example, good

    class Picture
    {
        int mx;
        int my;
        vector<int> data;

        static int check_size(int size)
        {
            // invariant check
            Expects(size > 0);
            return size;
        }

    public:
        // even better would be a class for a 2D Size as one single parameter
        Picture(int x, int y)
            : mx(check_size(x))
            , my(check_size(y))
            // now we know x and y have a valid size
            , data(mx * my) // will throw std::bad_alloc on error
        {
            // picture is ready-to-use
        }

        // compiler generated dtor does the job. (also see C.21)

        // ...
    };

    Picture picture1(100, 100);
    // picture1 is ready-to-use here...

    // not a valid size for y,
    // default contract violation behavior will call std::terminate then
    Picture picture2(100, 0);
    // not reach here...

##### Alternative

* Always establish a class invariant in a constructor.
* Don't define an object before it is needed.

### <a name="Rnr-goto-exit"></a>NR.6: Don't place all cleanup actions at the end of a function and `goto exit`

##### Reason

`goto` is error-prone.
This technique is a pre-exception technique for RAII-like resource and error handling.

##### Example, bad

    void do_something(int n)
    {
        if (n < 100) goto exit;
        // ...
        int* p = (int*) malloc(n);
        // ...
        if (some_error) goto_exit;
        // ...
    exit:
        free(p);
    }

and spot the bug.

##### Alternative

* Use exceptions and [RAII](#Re-raii)
* for non-RAII resources, use [`finally`](#Re-finally).

### <a name="Rnr-protected-data"></a>NR.7: Don't make all data members `protected`

##### Reason

`protected` data is a source of errors.
`protected` data can be manipulated from an unbounded amount of code in various places.
`protected` data is the class hierarchy equivalent to global data.

##### Example

    ???

##### Alternative

* [Make member data `public` or (preferably) `private`](#Rh-protected)
