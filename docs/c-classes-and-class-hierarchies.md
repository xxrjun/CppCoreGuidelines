# C: Classes and class hierarchies {#S-class}

A class is a user-defined type, for which a programmer can define the representation, operations, and interfaces.
Class hierarchies are used to organize related classes into hierarchical structures.

Class rule summary:

* [C.1: Organize related data into structures (`struct`s or `class`es)](#Rc-org)
* [C.2: Use `class` if the class has an invariant; use `struct` if the data members can vary independently](#Rc-struct)
* [C.3: Represent the distinction between an interface and an implementation using a class](#Rc-interface)
* [C.4: Make a function a member only if it needs direct access to the representation of a class](#Rc-member)
* [C.5: Place helper functions in the same namespace as the class they support](#Rc-helper)
* [C.7: Don't define a class or enum and declare a variable of its type in the same statement](#Rc-standalone)
* [C.8: Use `class` rather than `struct` if any member is non-public](#Rc-class)
* [C.9: Minimize exposure of members](#Rc-private)

Subsections:

* [C.concrete: Concrete types](#SS-concrete)
* [C.ctor: Constructors, assignments, and destructors](#S-ctor)
* [C.con: Containers and other resource handles](#SS-containers)
* [C.lambdas: Function objects and lambdas](#SS-lambdas)
* [C.hier: Class hierarchies (OOP)](#SS-hier)
* [C.over: Overloading and overloaded operators](#SS-overload)
* [C.union: Unions](#SS-union)

### <a name="Rc-org"></a>C.1: Organize related data into structures (`struct`s or `class`es)

##### Reason

Ease of comprehension.
If data is related (for fundamental reasons), that fact should be reflected in code.

##### Example

    void draw(int x, int y, int x2, int y2);  // BAD: unnecessary implicit relationships
    void draw(Point from, Point to);          // better

##### Note

A simple class without virtual functions implies no space or time overhead.

##### Note

From a language perspective `class` and `struct` differ only in the default visibility of their members.

##### Enforcement

Probably impossible. Maybe a heuristic looking for data items used together is possible.

### <a name="Rc-struct"></a>C.2: Use `class` if the class has an invariant; use `struct` if the data members can vary independently

##### Reason

Readability.
Ease of comprehension.
The use of `class` alerts the programmer to the need for an invariant.
This is a useful convention.

##### Note

An invariant is a logical condition for the members of an object that a constructor must establish for the public member functions to assume.
After the invariant is established (typically by a constructor) every member function can be called for the object.
An invariant can be stated informally (e.g., in a comment) or more formally using `Expects`.

If all data members can vary independently of each other, no invariant is possible.

##### Example

    struct Pair {  // the members can vary independently
        string name;
        int volume;
    };

but:

    class Date {
    public:
        // validate that {yy, mm, dd} is a valid date and initialize
        Date(int yy, Month mm, char dd);
        // ...
    private:
        int y;
        Month m;
        char d;    // day
    };

##### Note

If a class has any `private` data, a user cannot completely initialize an object without the use of a constructor.
Hence, the class definer will provide a constructor and must specify its meaning.
This effectively means the definer need to define an invariant.

**See also**:

* [define a class with private data as `class`](#Rc-class)
* [Prefer to place the interface first in a class](#Rl-order)
* [minimize exposure of members](#Rc-private)
* [Avoid `protected` data](#Rh-protected)

##### Enforcement

Look for `struct`s with all data private and `class`es with public members.

### <a name="Rc-interface"></a>C.3: Represent the distinction between an interface and an implementation using a class

##### Reason

An explicit distinction between interface and implementation improves readability and simplifies maintenance.

##### Example

    class Date {
    public:
        Date();
        // validate that {yy, mm, dd} is a valid date and initialize
        Date(int yy, Month mm, char dd);

        int day() const;
        Month month() const;
        // ...
    private:
        // ... some representation ...
    };

For example, we can now change the representation of a `Date` without affecting its users (recompilation is likely, though).

##### Note

Using a class in this way to represent the distinction between interface and implementation is of course not the only way.
For example, we can use a set of declarations of freestanding functions in a namespace, an abstract base class, or a function template with concepts to represent an interface.
The most important issue is to explicitly distinguish between an interface and its implementation "details."
Ideally, and typically, an interface is far more stable than its implementation(s).

##### Enforcement

???

### <a name="Rc-member"></a>C.4: Make a function a member only if it needs direct access to the representation of a class

##### Reason

Less coupling than with member functions, fewer functions that can cause trouble by modifying object state, reduces the number of functions that needs to be modified after a change in representation.

##### Example

    class Date {
        // ... relatively small interface ...
    };

    // helper functions:
    Date next_weekday(Date);
    bool operator==(Date, Date);

The "helper functions" have no need for direct access to the representation of a `Date`.

##### Note

This rule becomes even better if C++ gets ["uniform function call"](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0251r0.pdf).

##### Exception

The language requires `virtual` functions to be members, and not all `virtual` functions directly access data.
In particular, members of an abstract class rarely do.

Note [multi-methods](https://web.archive.org/web/20200605021759/https://parasol.tamu.edu/~yuriys/papers/OMM10.pdf).

##### Exception

The language requires operators `=`, `()`, `[]`, and `->` to be members.

##### Exception

An overload set could have some members that do not directly access `private` data:

    class Foobar {
    public:
        void foo(long x) { /* manipulate private data */ }
        void foo(double x) { foo(std::lround(x)); }
        // ...
    private:
        // ...
    };

##### Exception

Similarly, a set of functions could be designed to be used in a chain:

    x.scale(0.5).rotate(45).set_color(Color::red);

Typically, some but not all of such functions directly access `private` data.

##### Enforcement

* Look for non-`virtual` member functions that do not touch data members directly.
The snag is that many member functions that do not need to touch data members directly do.
* Ignore `virtual` functions.
* Ignore functions that are part of an overload set out of which at least one function accesses `private` members.
* Ignore functions returning `this`.

### <a name="Rc-helper"></a>C.5: Place helper functions in the same namespace as the class they support

##### Reason

A helper function is a function (usually supplied by the writer of a class) that does not need direct access to the representation of the class, yet is seen as part of the useful interface to the class.
Placing them in the same namespace as the class makes their relationship to the class obvious and allows them to be found by argument dependent lookup.

##### Example

    namespace Chrono { // here we keep time-related services

        class Time { /* ... */ };
        class Date { /* ... */ };

        // helper functions:
        bool operator==(Date, Date);
        Date next_weekday(Date);
        // ...
    }

##### Note

This is especially important for [overloaded operators](#Ro-namespace).

##### Enforcement

* Flag global functions taking argument types from a single namespace.

### <a name="Rc-standalone"></a>C.7: Don't define a class or enum and declare a variable of its type in the same statement

##### Reason

Mixing a type definition and the definition of another entity in the same declaration is confusing and unnecessary.

##### Example, bad

    struct Data { /*...*/ } data{ /*...*/ };

##### Example, good

    struct Data { /*...*/ };
    Data data{ /*...*/ };

##### Enforcement

* Flag if the `}` of a class or enumeration definition is not followed by a `;`. The `;` is missing.

### <a name="Rc-class"></a>C.8: Use `class` rather than `struct` if any member is non-public

##### Reason

Readability.
To make it clear that something is being hidden/abstracted.
This is a useful convention.

##### Example, bad

    struct Date {
        int d, m;

        Date(int i, Month m);
        // ... lots of functions ...
    private:
        int y;  // year
    };

There is nothing wrong with this code as far as the C++ language rules are concerned,
but nearly everything is wrong from a design perspective.
The private data is hidden far from the public data.
The data is split in different parts of the class declaration.
Different parts of the data have different access.
All of this decreases readability and complicates maintenance.

##### Note

Prefer to place the interface first in a class, [see NL.16](#Rl-order).

##### Enforcement

Flag classes declared with `struct` if there is a `private` or `protected` member.

### <a name="Rc-private"></a>C.9: Minimize exposure of members

##### Reason

Encapsulation.
Information hiding.
Minimize the chance of unintended access.
This simplifies maintenance.

##### Example

    template<typename T, typename U>
    struct pair {
        T a;
        U b;
        // ...
    };

Whatever we do in the `//`-part, an arbitrary user of a `pair` can arbitrarily and independently change its `a` and `b`.
In a large code base, we cannot easily find which code does what to the members of `pair`.
This might be exactly what we want, but if we want to enforce a relation among members, we need to make them `private`
and enforce that relation (invariant) through constructors and member functions.
For example:

    class Distance {
    public:
        // ...
        double meters() const { return magnitude*unit; }
        void set_unit(double u)
        {
                // ... check that u is a factor of 10 ...
                // ... change magnitude appropriately ...
                unit = u;
        }
        // ...
    private:
        double magnitude;
        double unit;    // 1 is meters, 1000 is kilometers, 0.001 is millimeters, etc.
    };

##### Note

If the set of direct users of a set of variables cannot be easily determined, the type or usage of that set cannot be (easily) changed/improved.
For `public` and `protected` data, that's usually the case.

##### Example

A class can provide two interfaces to its users.
One for derived classes (`protected`) and one for general users (`public`).
For example, a derived class might be allowed to skip a run-time check because it has already guaranteed correctness:

    class Foo {
    public:
        int bar(int x) { check(x); return do_bar(x); }
        // ...
    protected:
        int do_bar(int x); // do some operation on the data
        // ...
    private:
        // ... data ...
    };

    class Dir : public Foo {
        //...
        int mem(int x, int y)
        {
            /* ... do something ... */
            return do_bar(x + y); // OK: derived class can bypass check
        }
    };

    void user(Foo& x)
    {
        int r1 = x.bar(1);      // OK, will check
        int r2 = x.do_bar(2);   // error: would bypass check
        // ...
    }

##### Note

[`protected` data is a bad idea](#Rh-protected).

##### Note

Prefer the order `public` members before `protected` members before `private` members; see [NL.16](#Rl-order).

##### Enforcement

* [Flag protected data](#Rh-protected).
* Flag mixtures of `public` and `private` data

## <a name="SS-concrete"></a>C.concrete: Concrete types

Concrete type rule summary:

* [C.10: Prefer concrete types over class hierarchies](#Rc-concrete)
* [C.11: Make concrete types regular](#Rc-regular)
* [C.12: Don't make data members `const` or references in a copyable or movable type](#Rc-constref)


### <a name="Rc-concrete"></a>C.10: Prefer concrete types over class hierarchies

##### Reason

A concrete type is fundamentally simpler than a type in a class hierarchy:
easier to design, easier to implement, easier to use, easier to reason about, smaller, and faster.
You need a reason (use cases) for using a hierarchy.

##### Example

    class Point1 {
        int x, y;
        // ... operations ...
        // ... no virtual functions ...
    };

    class Point2 {
        int x, y;
        // ... operations, some virtual ...
        virtual ~Point2();
    };

    void use()
    {
        Point1 p11 {1, 2};   // make an object on the stack
        Point1 p12 {p11};    // a copy

        auto p21 = make_unique<Point2>(1, 2);   // make an object on the free store
        auto p22 = p21->clone();                // make a copy
        // ...
    }

If a class is part of a hierarchy, we (in real code if not necessarily in small examples) must manipulate its objects through pointers or references.
That implies more memory overhead, more allocations and deallocations, and more run-time overhead to perform the resulting indirections.

##### Note

Concrete types can be stack-allocated and be members of other classes.

##### Note

The use of indirection is fundamental for run-time polymorphic interfaces.
The allocation/deallocation overhead is not (that's just the most common case).
We can use a base class as the interface of a scoped object of a derived class.
This is done where dynamic allocation is prohibited (e.g. hard-real-time) and to provide a stable interface to some kinds of plug-ins.


##### Enforcement

???


### <a name="Rc-regular"></a>C.11: Make concrete types regular

##### Reason

Regular types are easier to understand and reason about than types that are not regular (irregularities requires extra effort to understand and use).

The C++ built-in types are regular, and so are standard-library classes such as `string`, `vector`, and `map`. Concrete classes without assignment and equality can be defined, but they are (and should be) rare.

##### Example

    struct Bundle {
        string name;
        vector<Record> vr;
    };

    bool operator==(const Bundle& a, const Bundle& b)
    {
        return a.name == b.name && a.vr == b.vr;
    }

    Bundle b1 { "my bundle", {r1, r2, r3}};
    Bundle b2 = b1;
    if (!(b1 == b2)) error("impossible!");
    b2.name = "the other bundle";
    if (b1 == b2) error("No!");

In particular, if a concrete type is copyable, prefer to also give it an equality comparison operator, and ensure that `a = b` implies `a == b`.

##### Note

For structs intended to be shared with C code, defining `operator==` may not be feasible.

##### Note

Handles for resources that cannot be cloned, e.g., a `scoped_lock` for a `mutex`, are concrete types but typically cannot be copied (instead, they can usually be moved),
so they can't be regular; instead, they tend to be move-only.

##### Enforcement

???


### <a name="Rc-constref"></a>C.12: Don't make data members `const` or references in a copyable or movable type

##### Reason

`const` and reference data members are not useful in a copyable or movable type, and make such types difficult to use by making them at least partly uncopyable/unmovable for subtle reasons.

##### Example; bad

    class bad {
        const int i;    // bad
        string& s;      // bad
        // ...
    };

The `const` and `&` data members make this class "only-sort-of-copyable" -- copy-constructible but not copy-assignable.

##### Note

If you need a member to point to something, use a pointer (raw or smart, and `gsl::not_null` if it should not be null) instead of a reference.

##### Enforcement

Flag a data member that is `const`, `&`, or `&&` in a type that has any copy or move operation.



## <a name="S-ctor"></a>C.ctor: Constructors, assignments, and destructors

These functions control the lifecycle of objects: creation, copy, move, and destruction.
Define constructors to guarantee and simplify initialization of classes.

These are *default operations*:

* a default constructor: `X()`
* a copy constructor: `X(const X&)`
* a copy assignment: `operator=(const X&)`
* a move constructor: `X(X&&)`
* a move assignment: `operator=(X&&)`
* a destructor: `~X()`

By default, the compiler defines each of these operations if it is used, but the default can be suppressed.

The default operations are a set of related operations that together implement the lifecycle semantics of an object.
By default, C++ treats classes as value-like types, but not all types are value-like.

Set of default operations rules:

* [C.20: If you can avoid defining any default operations, do](#Rc-zero)
* [C.21: If you define or `=delete` any copy, move, or destructor function, define or `=delete` them all](#Rc-five)
* [C.22: Make default operations consistent](#Rc-matched)

Destructor rules:

* [C.30: Define a destructor if a class needs an explicit action at object destruction](#Rc-dtor)
* [C.31: All resources acquired by a class must be released by the class's destructor](#Rc-dtor-release)
* [C.32: If a class has a raw pointer (`T*`) or reference (`T&`), consider whether it might be owning](#Rc-dtor-ptr)
* [C.33: If a class has an owning pointer member, define a destructor](#Rc-dtor-ptr2)
* [C.35: A base class destructor should be either public and virtual, or protected and non-virtual](#Rc-dtor-virtual)
* [C.36: A destructor must not fail](#Rc-dtor-fail)
* [C.37: Make destructors `noexcept`](#Rc-dtor-noexcept)

Constructor rules:

* [C.40: Define a constructor if a class has an invariant](#Rc-ctor)
* [C.41: A constructor should create a fully initialized object](#Rc-complete)
* [C.42: If a constructor cannot construct a valid object, throw an exception](#Rc-throw)
* [C.43: Ensure that a copyable class has a default constructor](#Rc-default0)
* [C.44: Prefer default constructors to be simple and non-throwing](#Rc-default00)
* [C.45: Don't define a default constructor that only initializes data members; use member initializers instead](#Rc-default)
* [C.46: By default, declare single-argument constructors `explicit`](#Rc-explicit)
* [C.47: Define and initialize data members in the order of member declaration](#Rc-order)
* [C.48: Prefer default member initializers to member initializers in constructors for constant initializers](#Rc-in-class-initializer)
* [C.49: Prefer initialization to assignment in constructors](#Rc-initialize)
* [C.50: Use a factory function if you need "virtual behavior" during initialization](#Rc-factory)
* [C.51: Use delegating constructors to represent common actions for all constructors of a class](#Rc-delegating)
* [C.52: Use inheriting constructors to import constructors into a derived class that does not need further explicit initialization](#Rc-inheriting)

Copy and move rules:

* [C.60: Make copy assignment non-`virtual`, take the parameter by `const&`, and return by non-`const&`](#Rc-copy-assignment)
* [C.61: A copy operation should copy](#Rc-copy-semantic)
* [C.62: Make copy assignment safe for self-assignment](#Rc-copy-self)
* [C.63: Make move assignment non-`virtual`, take the parameter by `&&`, and return by non-`const&`](#Rc-move-assignment)
* [C.64: A move operation should move and leave its source in a valid state](#Rc-move-semantic)
* [C.65: Make move assignment safe for self-assignment](#Rc-move-self)
* [C.66: Make move operations `noexcept`](#Rc-move-noexcept)
* [C.67: A polymorphic class should suppress public copy/move](#Rc-copy-virtual)

Other default operations rules:

* [C.80: Use `=default` if you have to be explicit about using the default semantics](#Rc-eqdefault)
* [C.81: Use `=delete` when you want to disable default behavior (without wanting an alternative)](#Rc-delete)
* [C.82: Don't call virtual functions in constructors and destructors](#Rc-ctor-virtual)
* [C.83: For value-like types, consider providing a `noexcept` swap function](#Rc-swap)
* [C.84: A `swap` must not fail](#Rc-swap-fail)
* [C.85: Make `swap` `noexcept`](#Rc-swap-noexcept)
* [C.86: Make `==` symmetric with respect of operand types and `noexcept`](#Rc-eq)
* [C.87: Beware of `==` on base classes](#Rc-eq-base)
* [C.89: Make a `hash` `noexcept`](#Rc-hash)
* [C.90: Rely on constructors and assignment operators, not memset and memcpy](#Rc-memset)

## <a name="SS-defop"></a>C.defop: Default Operations

By default, the language supplies the default operations with their default semantics.
However, a programmer can disable or replace these defaults.

### <a name="Rc-zero"></a>C.20: If you can avoid defining default operations, do

##### Reason

It's the simplest and gives the cleanest semantics.

##### Example

    struct Named_map {
    public:
        explicit Named_map(const string& n) : name(n) {}
        // no copy/move constructors
        // no copy/move assignment operators
        // no destructor
    private:
        string name;
        map<int, int> rep;
    };

    Named_map nm("map"); // construct
    Named_map nm2 {nm};  // copy construct

Since `std::map` and `string` have all the special functions, no further work is needed.

##### Note

This is known as "the rule of zero".

##### Enforcement

(Not enforceable) While not enforceable, a good static analyzer can detect patterns that indicate a possible improvement to meet this rule.
For example, a class with a (pointer, size) pair of members and a destructor that `delete`s the pointer could probably be converted to a `vector`.

### <a name="Rc-five"></a>C.21: If you define or `=delete` any copy, move, or destructor function, define or `=delete` them all

##### Reason

The semantics of copy, move, and destruction are closely related, so if one needs to be declared, the odds are that others need consideration too.

Declaring any copy/move/destructor function,
even as `=default` or `=delete`, will suppress the implicit declaration
of a move constructor and move assignment operator.
Declaring a move constructor or move assignment operator, even as
`=default` or `=delete`, will cause an implicitly generated copy constructor
or implicitly generated copy assignment operator to be defined as deleted.
So as soon as any of these are declared, the others should
all be declared to avoid unwanted effects like turning all potential moves
into more expensive copies, or making a class move-only.

##### Example, bad

    struct M2 {   // bad: incomplete set of copy/move/destructor operations
    public:
        // ...
        // ... no copy or move operations ...
        ~M2() { delete[] rep; }
    private:
        pair<int, int>* rep;  // zero-terminated set of pairs
    };

    void use()
    {
        M2 x;
        M2 y;
        // ...
        x = y;   // the default assignment
        // ...
    }

Given that "special attention" was needed for the destructor (here, to deallocate), the likelihood that the implicitly-defined copy and move assignment operators will be correct is low (here, we would get double deletion).

##### Note

This is known as "the rule of five."

##### Note

If you want a default implementation (while defining another), write `=default` to show you're doing so intentionally for that function.
If you don't want a generated default function, suppress it with `=delete`.

##### Example, good

When a destructor needs to be declared just to make it `virtual`, it can be
defined as defaulted.

    class AbstractBase {
    public:
        virtual void foo() = 0;  // at least one abstract method to make the class abstract
        virtual ~AbstractBase() = default;
        // ...
    };

To prevent slicing as per [C.67](#Rc-copy-virtual),
make the copy and move operations protected or `=delete`d, and add a `clone`:

    class CloneableBase {
    public:
        virtual unique_ptr<CloneableBase> clone() const;
        virtual ~CloneableBase() = default;
        CloneableBase() = default;
        CloneableBase(const CloneableBase&) = delete;
        CloneableBase& operator=(const CloneableBase&) = delete;
        CloneableBase(CloneableBase&&) = delete;
        CloneableBase& operator=(CloneableBase&&) = delete;
        // ... other constructors and functions ...
    };

Defining only the move operations or only the copy operations would have the
same effect here, but stating the intent explicitly for each special member
makes it more obvious to the reader.

##### Note

Compilers enforce much of this rule and ideally warn about any violation.

##### Note

Relying on an implicitly generated copy operation in a class with a destructor is deprecated.

##### Note

Writing these functions can be error-prone.
Note their argument types:

    class X {
    public:
        // ...
        virtual ~X() = default;               // destructor (virtual if X is meant to be a base class)
        X(const X&) = default;                // copy constructor
        X& operator=(const X&) = default;     // copy assignment
        X(X&&) noexcept = default;            // move constructor
        X& operator=(X&&) noexcept = default; // move assignment
    };

A minor mistake (such as a misspelling, leaving out a `const`, using `&` instead of `&&`, or leaving out a special function) can lead to errors or warnings.
To avoid the tedium and the possibility of errors, try to follow the [rule of zero](#Rc-zero).

##### Enforcement

(Simple) A class should have a declaration (even a `=delete` one) for either all or none of the copy/move/destructor functions.

### <a name="Rc-matched"></a>C.22: Make default operations consistent

##### Reason

The default operations are conceptually a matched set. Their semantics are interrelated.
Users will be surprised if copy/move construction and copy/move assignment do logically different things. Users will be surprised if constructors and destructors do not provide a consistent view of resource management. Users will be surprised if copy and move don't reflect the way constructors and destructors work.

##### Example, bad

    class Silly {   // BAD: Inconsistent copy operations
        class Impl {
            // ...
        };
        shared_ptr<Impl> p;
    public:
        Silly(const Silly& a) : p(make_shared<Impl>()) { *p = *a.p; }   // deep copy
        Silly& operator=(const Silly& a) { p = a.p; return *this; }   // shallow copy
        // ...
    };

These operations disagree about copy semantics. This will lead to confusion and bugs.

##### Enforcement

* (Complex) A copy/move constructor and the corresponding copy/move assignment operator should write to the same data members at the same level of dereference.
* (Complex) Any data members written in a copy/move constructor should also be initialized by all other constructors.
* (Complex) If a copy/move constructor performs a deep copy of a data member, then the destructor should modify the data member.
* (Complex) If a destructor is modifying a data member, that data member should be written in any copy/move constructors or assignment operators.

## <a name="SS-dtor"></a>C.dtor: Destructors

"Does this class need a destructor?" is a surprisingly insightful design question.
For most classes the answer is "no" either because the class holds no resources or because destruction is handled by [the rule of zero](#Rc-zero);
that is, its members can take care of themselves as concerns destruction.
If the answer is "yes", much of the design of the class follows (see [the rule of five](#Rc-five)).

### <a name="Rc-dtor"></a>C.30: Define a destructor if a class needs an explicit action at object destruction

##### Reason

A destructor is implicitly invoked at the end of an object's lifetime.
If the default destructor is sufficient, use it.
Only define a non-default destructor if a class needs to execute code that is not already part of its members' destructors.

##### Example

    template<typename A>
    struct final_action {   // slightly simplified
        A act;
        final_action(A a) : act{a} {}
        ~final_action() { act(); }
    };

    template<typename A>
    final_action<A> finally(A act)   // deduce action type
    {
        return final_action<A>{act};
    }

    void test()
    {
        auto act = finally([] { cout << "Exit test\n"; });  // establish exit action
        // ...
        if (something) return;   // act done here
        // ...
    } // act done here

The whole purpose of `final_action` is to get a piece of code (usually a lambda) executed upon destruction.

##### Note

There are two general categories of classes that need a user-defined destructor:

* A class with a resource that is not already represented as a class with a destructor, e.g., a `vector` or a transaction class.
* A class that exists primarily to execute an action upon destruction, such as a tracer or `final_action`.

##### Example, bad

    class Foo {   // bad; use the default destructor
    public:
        // ...
        ~Foo() { s = ""; i = 0; vi.clear(); }  // clean up
    private:
        string s;
        int i;
        vector<int> vi;
    };

The default destructor does it better, more efficiently, and can't get it wrong.

##### Enforcement

Look for likely "implicit resources", such as pointers and references. Look for classes with destructors even though all their data members have destructors.

### <a name="Rc-dtor-release"></a>C.31: All resources acquired by a class must be released by the class's destructor

##### Reason

Prevention of resource leaks, especially in error cases.

##### Note

For resources represented as classes with a complete set of default operations, this happens automatically.

##### Example

    class X {
        ifstream f;   // might own a file
        // ... no default operations defined or =deleted ...
    };

`X`'s `ifstream` implicitly closes any file it might have open upon destruction of its `X`.

##### Example, bad

    class X2 {     // bad
        FILE* f;   // might own a file
        // ... no default operations defined or =deleted ...
    };

`X2` might leak a file handle.

##### Note

What about a socket that won't close? A destructor, close, or cleanup operation [should never fail](#Rc-dtor-fail).
If it does nevertheless, we have a problem that has no really good solution.
For starters, the writer of a destructor does not know why the destructor is called and cannot "refuse to act" by throwing an exception.
See [discussion](#Sd-never-fail).
To make the problem worse, many "close/release" operations are not retryable.
Many have tried to solve this problem, but no general solution is known.
If at all possible, consider failure to close/cleanup a fundamental design error and terminate.

##### Note

A class can hold pointers and references to objects that it does not own.
Obviously, such objects should not be `delete`d by the class's destructor.
For example:

    Preprocessor pp { /* ... */ };
    Parser p { pp, /* ... */ };
    Type_checker tc { p, /* ... */ };

Here `p` refers to `pp` but does not own it.

##### Enforcement

* (Simple) If a class has pointer or reference members that are owners
  (e.g., deemed owners by using `gsl::owner`), then they should be referenced in its destructor.
* (Hard) Determine if pointer or reference members are owners when there is no explicit statement of ownership
  (e.g., look into the constructors).

### <a name="Rc-dtor-ptr"></a>C.32: If a class has a raw pointer (`T*`) or reference (`T&`), consider whether it might be owning

##### Reason

There is a lot of code that is non-specific about ownership.

##### Example

    class legacy_class
    {
        foo* m_owning;   // Bad: change to unique_ptr<T> or owner<T*>
        bar* m_observer; // OK: keep
    }

The only way to determine ownership may be code analysis.

##### Note

Ownership should be clear in new code (and refactored legacy code) according to [R.20](#Rr-owner) for owning
pointers and [R.3](#Rr-ptr) for non-owning pointers.  References should never own [R.4](#Rr-ref).

##### Enforcement

Look at the initialization of raw member pointers and member references and see if an allocation is used.

### <a name="Rc-dtor-ptr2"></a>C.33: If a class has an owning pointer member, define a destructor

##### Reason

An owned object must be `deleted` upon destruction of the object that owns it.

##### Example

A pointer member could represent a resource.
[A `T*` should not do so](#Rr-ptr), but in older code, that's common.
Consider a `T*` a possible owner and therefore suspect.

    template<typename T>
    class Smart_ptr {
        T* p;   // BAD: vague about ownership of *p
        // ...
    public:
        // ... no user-defined default operations ...
    };

    void use(Smart_ptr<int> p1)
    {
        // error: p2.p leaked (if not nullptr and not owned by some other code)
        auto p2 = p1;
    }

Note that if you define a destructor, you must define or delete [all default operations](#Rc-five):

    template<typename T>
    class Smart_ptr2 {
        T* p;   // BAD: vague about ownership of *p
        // ...
    public:
        // ... no user-defined copy operations ...
        ~Smart_ptr2() { delete p; }  // p is an owner!
    };

    void use(Smart_ptr2<int> p1)
    {
        auto p2 = p1;   // error: double deletion
    }

The default copy operation will just copy the `p1.p` into `p2.p` leading to a double destruction of `p1.p`. Be explicit about ownership:

    template<typename T>
    class Smart_ptr3 {
        owner<T*> p;   // OK: explicit about ownership of *p
        // ...
    public:
        // ...
        // ... copy and move operations ...
        ~Smart_ptr3() { delete p; }
    };

    void use(Smart_ptr3<int> p1)
    {
        auto p2 = p1;   // OK: no double deletion
    }

##### Note

Often the simplest way to get a destructor is to replace the pointer with a smart pointer (e.g., `std::unique_ptr`) and let the compiler arrange for proper destruction to be done implicitly.

##### Note

Why not just require all owning pointers to be "smart pointers"?
That would sometimes require non-trivial code changes and might affect ABIs.

##### Enforcement

* A class with a pointer data member is suspect.
* A class with an `owner<T>` should define its default operations.


### <a name="Rc-dtor-virtual"></a>C.35: A base class destructor should be either public and virtual, or protected and non-virtual

##### Reason

To prevent undefined behavior.
If the destructor is public, then calling code can attempt to destroy a derived class object through a base class pointer, and the result is undefined if the base class's destructor is non-virtual.
If the destructor is protected, then calling code cannot destroy through a base class pointer and the destructor does not need to be virtual; it does need to be protected, not private, so that derived destructors can invoke it.
In general, the writer of a base class does not know the appropriate action to be done upon destruction.

##### Discussion

See [this in the Discussion section](#Sd-dtor).

##### Example, bad

    struct Base {  // BAD: implicitly has a public non-virtual destructor
        virtual void f();
    };

    struct D : Base {
        string s {"a resource needing cleanup"};
        ~D() { /* ... do some cleanup ... */ }
        // ...
    };

    void use()
    {
        unique_ptr<Base> p = make_unique<D>();
        // ...
    } // p's destruction calls ~Base(), not ~D(), which leaks D::s and possibly more

##### Note

A virtual function defines an interface to derived classes that can be used without looking at the derived classes.
If the interface allows destroying, it should be safe to do so.

##### Note

A destructor must be non-private or it will prevent using the type:

    class X {
        ~X();   // private destructor
        // ...
    };

    void use()
    {
        X a;                        // error: cannot destroy
        auto p = make_unique<X>();  // error: cannot destroy
    }

##### Exception

We can imagine one case where you could want a protected virtual destructor: When an object of a derived type (and only of such a type) should be allowed to destroy *another* object (not itself) through a pointer to base. We haven't seen such a case in practice, though.


##### Enforcement

* A class with any virtual functions should have a destructor that is either public and virtual or else protected and non-virtual.
* If a class inherits publicly from a base class, the base class should have a destructor that is either public and virtual or else protected and non-virtual.

### <a name="Rc-dtor-fail"></a>C.36: A destructor must not fail

##### Reason

In general we do not know how to write error-free code if a destructor should fail.
The standard library requires that all classes it deals with have destructors that do not exit by throwing.

##### Example

    class X {
    public:
        ~X() noexcept;
        // ...
    };

    X::~X() noexcept
    {
        // ...
        if (cannot_release_a_resource) terminate();
        // ...
    }

##### Note

Many have tried to devise a fool-proof scheme for dealing with failure in destructors.
None have succeeded to come up with a general scheme.
This can be a real practical problem: For example, what about a socket that won't close?
The writer of a destructor does not know why the destructor is called and cannot "refuse to act" by throwing an exception.
See [discussion](#Sd-never-fail).
To make the problem worse, many "close/release" operations are not retryable.
If at all possible, consider failure to close/cleanup a fundamental design error and terminate.

##### Note

Declare a destructor `noexcept`. That will ensure that it either completes normally or terminates the program.

##### Note

If a resource cannot be released and the program must not fail, try to signal the failure to the rest of the system somehow
(maybe even by modifying some global state and hope something will notice and be able to take care of the problem).
Be fully aware that this technique is special-purpose and error-prone.
Consider the "my connection will not close" example.
Probably there is a problem at the other end of the connection and only a piece of code responsible for both ends of the connection can properly handle the problem.
The destructor could send a message (somehow) to the responsible part of the system, consider that to have closed the connection, and return normally.

##### Note

If a destructor uses operations that could fail, it can catch exceptions and in some cases still complete successfully
(e.g., by using a different clean-up mechanism from the one that threw an exception).

##### Enforcement

(Simple) A destructor should be declared `noexcept` if it could throw.

### <a name="Rc-dtor-noexcept"></a>C.37: Make destructors `noexcept`

##### Reason

 [A destructor must not fail](#Rc-dtor-fail). If a destructor tries to exit with an exception, it's a bad design error and the program had better terminate.

##### Note

A destructor (either user-defined or compiler-generated) is implicitly declared `noexcept` (independently of what code is in its body) if all of the members of its class have `noexcept` destructors. By explicitly marking destructors `noexcept`, an author guards against the destructor becoming implicitly `noexcept(false)` through the addition or modification of a class member.

##### Example

Not all destructors are noexcept by default; one throwing member poisons the whole class hierarchy

    struct X {
        Details x;  // happens to have a throwing destructor
        // ...
        ~X() { }    // implicitly noexcept(false); aka can throw
    };

So, if in doubt, declare a destructor noexcept.

##### Note

Why not then declare all destructors noexcept?
Because that would in many cases -- especially simple cases -- be distracting clutter.

##### Enforcement

(Simple) A destructor should be declared `noexcept` if it could throw.

## <a name="SS-ctor"></a>C.ctor: Constructors

A constructor defines how an object is initialized (constructed).

### <a name="Rc-ctor"></a>C.40: Define a constructor if a class has an invariant

##### Reason

That's what constructors are for.

##### Example

    class Date {  // a Date represents a valid date
                  // in the January 1, 1900 to December 31, 2100 range
        Date(int dd, int mm, int yy)
            :d{dd}, m{mm}, y{yy}
        {
            if (!is_valid(d, m, y)) throw Bad_date{};  // enforce invariant
        }
        // ...
    private:
        int d, m, y;
    };

It is often a good idea to express the invariant as an `Ensures` on the constructor.

##### Note

A constructor can be used for convenience even if a class does not have an invariant. For example:

    struct Rec {
        string s;
        int i {0};
        Rec(const string& ss) : s{ss} {}
        Rec(int ii) :i{ii} {}
    };

    Rec r1 {7};
    Rec r2 {"Foo bar"};

##### Note

The C++11 initializer list rule eliminates the need for many constructors. For example:

    struct Rec2{
        string s;
        int i;
        Rec2(const string& ss, int ii = 0) :s{ss}, i{ii} {}   // redundant
    };

    Rec2 r1 {"Foo", 7};
    Rec2 r2 {"Bar"};

The `Rec2` constructor is redundant.
Also, the default for `int` would be better done as a [default member initializer](#Rc-in-class-initializer).

**See also**: [construct valid object](#Rc-complete) and [constructor throws](#Rc-throw).

##### Enforcement

* Flag classes with user-defined copy operations but no constructor (a user-defined copy is a good indicator that the class has an invariant)

### <a name="Rc-complete"></a>C.41: A constructor should create a fully initialized object

##### Reason

A constructor establishes the invariant for a class. A user of a class should be able to assume that a constructed object is usable.

##### Example, bad

    class X1 {
        FILE* f;   // call init() before any other function
        // ...
    public:
        X1() {}
        void init();   // initialize f
        void read();   // read from f
        // ...
    };

    void f()
    {
        X1 file;
        file.read();   // crash or bad read!
        // ...
        file.init();   // too late
        // ...
    }

Compilers do not read comments.

##### Exception

If a valid object cannot conveniently be constructed by a constructor, [use a factory function](#Rc-factory).

##### Enforcement

* (Simple) Every constructor should initialize every data member (either explicitly, via a delegating ctor call or via default construction).
* (Unknown) If a constructor has an `Ensures` contract, try to see if it holds as a postcondition.

##### Note

If a constructor acquires a resource (to create a valid object), that resource should be [released by the destructor](#Rc-dtor-release).
The idiom of having constructors acquire resources and destructors release them is called [RAII](#Rr-raii) ("Resource Acquisition Is Initialization").

### <a name="Rc-throw"></a>C.42: If a constructor cannot construct a valid object, throw an exception

##### Reason

Leaving behind an invalid object is asking for trouble.

##### Example

    class X2 {
        FILE* f;
        // ...
    public:
        X2(const string& name)
            :f{fopen(name.c_str(), "r")}
        {
            if (!f) throw runtime_error{"could not open" + name};
            // ...
        }

        void read();      // read from f
        // ...
    };

    void f()
    {
        X2 file {"Zeno"}; // throws if file isn't open
        file.read();      // fine
        // ...
    }

##### Example, bad

    class X3 {     // bad: the constructor leaves a non-valid object behind
        FILE* f;   // call is_valid() before any other function
        bool valid;
        // ...
    public:
        X3(const string& name)
            :f{fopen(name.c_str(), "r")}, valid{false}
        {
            if (f) valid = true;
            // ...
        }

        bool is_valid() { return valid; }
        void read();   // read from f
        // ...
    };

    void f()
    {
        X3 file {"Heraclides"};
        file.read();   // crash or bad read!
        // ...
        if (file.is_valid()) {
            file.read();
            // ...
        }
        else {
            // ... handle error ...
        }
        // ...
    }

##### Note

For a variable definition (e.g., on the stack or as a member of another object) there is no explicit function call from which an error code could be returned.
Leaving behind an invalid object and relying on users to consistently check an `is_valid()` function before use is tedious, error-prone, and inefficient.

##### Exception

There are domains, such as some hard-real-time systems (think airplane controls) where (without additional tool support) exception handling is not sufficiently predictable from a timing perspective.
There the `is_valid()` technique must be used. In such cases, check `is_valid()` consistently and immediately to simulate [RAII](#Rr-raii).

##### Alternative

If you feel tempted to use some "post-constructor initialization" or "two-stage initialization" idiom, try not to do that.
If you really have to, look at [factory functions](#Rc-factory).

##### Note

One reason people have used `init()` functions rather than doing the initialization work in a constructor has been to avoid code replication.
[Delegating constructors](#Rc-delegating) and [default member initialization](#Rc-in-class-initializer) do that better.
Another reason has been to delay initialization until an object is needed; the solution to that is often [not to declare a variable until it can be properly initialized](#Res-init)

##### Enforcement

???

### <a name="Rc-default0"></a>C.43: Ensure that a copyable class has a default constructor

##### Reason

That is, ensure that if a concrete class is copyable it also satisfies the rest of "semiregular."

Many language and library facilities rely on default constructors to initialize their elements, e.g. `T a[10]` and `std::vector<T> v(10)`.
A default constructor often simplifies the task of defining a suitable [moved-from state](#???) for a type that is also copyable.

##### Example

    class Date { // BAD: no default constructor
    public:
        Date(int dd, int mm, int yyyy);
        // ...
    };

    vector<Date> vd1(1000);   // default Date needed here
    vector<Date> vd2(1000, Date{7, Month::October, 1885});   // alternative

The default constructor is only auto-generated if there is no user-declared constructor, hence it's impossible to initialize the vector `vd1` in the example above.
The absence of a default value can cause surprises for users and complicate its use, so if one can be reasonably defined, it should be.

`Date` is chosen to encourage thought:
There is no "natural" default date (the big bang is too far back in time to be useful for most people), so this example is non-trivial.
`{0, 0, 0}` is not a valid date in most calendar systems, so choosing that would be introducing something like floating-point's `NaN`.
However, most realistic `Date` classes have a "first date" (e.g. January 1, 1970 is popular), so making that the default is usually trivial.

    class Date {
    public:
        Date(int dd, int mm, int yyyy);
        Date() = default; // [See also](#Rc-default)
        // ...
    private:
        int dd {1};
        int mm {1};
        int yyyy {1970};
        // ...
    };

    vector<Date> vd1(1000);

##### Note

A class with members that all have default constructors implicitly gets a default constructor:

    struct X {
        string s;
        vector<int> v;
    };

    X x; // means X{ { }, { } }; that is the empty string and the empty vector

Beware that built-in types are not properly default constructed:

    struct X {
        string s;
        int i;
    };

    void f()
    {
        X x;    // x.s is initialized to the empty string; x.i is uninitialized

        cout << x.s << ' ' << x.i << '\n';
        ++x.i;
    }

Statically allocated objects of built-in types are by default initialized to `0`, but local built-in variables are not.
Beware that your compiler might default initialize local built-in variables, whereas an optimized build will not.
Thus, code like the example above might appear to work, but it relies on undefined behavior.
Assuming that you want initialization, an explicit default initialization can help:

    struct X {
        string s;
        int i {};   // default initialize (to 0)
    };

##### Notes

Classes that don't have a reasonable default construction are usually not copyable either, so they don't fall under this guideline.

For example, a base class should not be copyable, and so does not necessarily need a default constructor:

    // Shape is an abstract base class, not a copyable type.
    // It might or might not need a default constructor.
    struct Shape {
        virtual void draw() = 0;
        virtual void rotate(int) = 0;
        // =delete copy/move functions
        // ...
    };

A class that must acquire a caller-provided resource during construction often cannot have a default constructor, but it does not fall under this guideline because such a class is usually not copyable anyway:

    // std::lock_guard is not a copyable type.
    // It does not have a default constructor.
    lock_guard g {mx};  // guard the mutex mx
    lock_guard g2;      // error: guarding nothing

A class that has a "special state" that must be handled separately from other states by member functions or users causes extra work
(and most likely more errors). Such a type can naturally use the special state as a default constructed value, whether or not it is copyable:

    // std::ofstream is not a copyable type.
    // It does happen to have a default constructor
    // that goes along with a special "not open" state.
    ofstream out {"Foobar"};
    // ...
    out << log(time, transaction);

Similar special-state types that are copyable, such as copyable smart pointers that have the special state "==nullptr", should use the special state as their default constructed value.

However, it is preferable to have a default constructor default to a meaningful state such as `std::string`s `""` and `std::vector`s `{}`.

##### Enforcement

* Flag classes that are copyable by `=` without a default constructor
* Flag classes that are comparable with `==` but not copyable


### <a name="Rc-default00"></a>C.44: Prefer default constructors to be simple and non-throwing

##### Reason

Being able to set a value to "the default" without operations that might fail simplifies error handling and reasoning about move operations.

##### Example, problematic

    template<typename T>
    // elem points to space-elem element allocated using new
    class Vector0 {
    public:
        Vector0() :Vector0{0} {}
        Vector0(int n) :elem{new T[n]}, space{elem + n}, last{elem} {}
        // ...
    private:
        own<T*> elem;
        T* space;
        T* last;
    };

This is nice and general, but setting a `Vector0` to empty after an error involves an allocation, which might fail.
Also, having a default `Vector` represented as `{new T[0], 0, 0}` seems wasteful.
For example, `Vector0<int> v[100]` costs 100 allocations.

##### Example

    template<typename T>
    // elem is nullptr or elem points to space-elem element allocated using new
    class Vector1 {
    public:
        // sets the representation to {nullptr, nullptr, nullptr}; doesn't throw
        Vector1() noexcept {}
        Vector1(int n) :elem{new T[n]}, space{elem + n}, last{elem} {}
        // ...
    private:
        own<T*> elem {};
        T* space {};
        T* last {};
    };

Using `{nullptr, nullptr, nullptr}` makes `Vector1{}` cheap, but a special case and implies run-time checks.
Setting a `Vector1` to empty after detecting an error is trivial.

##### Enforcement

* Flag throwing default constructors

### <a name="Rc-default"></a>C.45: Don't define a default constructor that only initializes data members; use default member initializers instead

##### Reason

Using default member initializers lets the compiler generate the function for you. The compiler-generated function can be more efficient.

##### Example, bad

    class X1 { // BAD: doesn't use member initializers
        string s;
        int i;
    public:
        X1() :s{"default"}, i{1} { }
        // ...
    };

##### Example

    class X2 {
        string s {"default"};
        int i {1};
    public:
        // use compiler-generated default constructor
        // ...
    };

##### Enforcement

(Simple) A default constructor should do more than just initialize data members with constants.

### <a name="Rc-explicit"></a>C.46: By default, declare single-argument constructors explicit

##### Reason

To avoid unintended conversions.

##### Example, bad

    class String {
    public:
        String(int);   // BAD
        // ...
    };

    String s = 10;   // surprise: string of size 10

##### Exception

If you really want an implicit conversion from the constructor argument type to the class type, don't use `explicit`:

    class Complex {
    public:
        Complex(double d);   // OK: we want a conversion from d to {d, 0}
        // ...
    };

    Complex z = 10.7;   // unsurprising conversion

**See also**: [Discussion of implicit conversions](#Ro-conversion)

##### Note

Copy and move constructors should not be made `explicit` because they do not perform conversions. Explicit copy/move constructors make passing and returning by value difficult.

##### Enforcement

(Simple) Single-argument constructors should be declared `explicit`. Good single argument non-`explicit` constructors are rare in most code bases. Warn for all that are not on a "positive list".

### <a name="Rc-order"></a>C.47: Define and initialize data members in the order of member declaration

##### Reason

To minimize confusion and errors. That is the order in which the initialization happens (independent of the order of member initializers).

##### Example, bad

    class Foo {
        int m1;
        int m2;
    public:
        Foo(int x) :m2{x}, m1{++x} { }   // BAD: misleading initializer order
        // ...
    };

    Foo x(1); // surprise: x.m1 == x.m2 == 2

##### Enforcement

(Simple) A member initializer list should mention the members in the same order they are declared.

**See also**: [Discussion](#Sd-order)

### <a name="Rc-in-class-initializer"></a>C.48: Prefer default member initializers to member initializers in constructors for constant initializers

##### Reason

Makes it explicit that the same value is expected to be used in all constructors. Avoids repetition. Avoids maintenance problems. It leads to the shortest and most efficient code.

##### Example, bad

    class X {   // BAD
        int i;
        string s;
        int j;
    public:
        X() :i{666}, s{"qqq"} { }   // j is uninitialized
        X(int ii) :i{ii} {}         // s is "" and j is uninitialized
        // ...
    };

How would a maintainer know whether `j` was deliberately uninitialized (probably a bad idea anyway) and whether it was intentional to give `s` the default value `""` in one case and `qqq` in another (almost certainly a bug)? The problem with `j` (forgetting to initialize a member) often happens when a new member is added to an existing class.

##### Example

    class X2 {
        int i {666};
        string s {"qqq"};
        int j {0};
    public:
        X2() = default;        // all members are initialized to their defaults
        X2(int ii) :i{ii} {}   // s and j initialized to their defaults
        // ...
    };

**Alternative**: We can get part of the benefits from default arguments to constructors, and that is not uncommon in older code. However, that is less explicit, causes more arguments to be passed, and is repetitive when there is more than one constructor:

    class X3 {   // BAD: inexplicit, argument passing overhead
        int i;
        string s;
        int j;
    public:
        X3(int ii = 666, const string& ss = "qqq", int jj = 0)
            :i{ii}, s{ss}, j{jj} { }   // all members are initialized to their defaults
        // ...
    };

##### Enforcement

* (Simple) Every constructor should initialize every data member (either explicitly, via a delegating ctor call or via default construction).
* (Simple) Default arguments to constructors suggest a default member initializer might be more appropriate.

### <a name="Rc-initialize"></a>C.49: Prefer initialization to assignment in constructors

##### Reason

An initialization explicitly states that initialization, rather than assignment, is done and can be more elegant and efficient. Prevents "use before set" errors.

##### Example, good

    class A {   // Good
        string s1;
    public:
        A(czstring p) : s1{p} { }    // GOOD: directly construct (and the C-string is explicitly named)
        // ...
    };

##### Example, bad

    class B {   // BAD
        string s1;
    public:
        B(const char* p) { s1 = p; }   // BAD: default constructor followed by assignment
        // ...
    };

    class C {   // UGLY, aka very bad
        int* p;
    public:
        C() { cout << *p; p = new int{10}; }   // accidental use before initialized
        // ...
    };

##### Example, better still

Instead of those `const char*`s we could use C++17 `std::string_view` or `gsl::span<char>`
as [a more general way to present arguments to a function](#Rstr-view):

    class D {   // Good
        string s1;
    public:
        D(string_view v) : s1{v} { }    // GOOD: directly construct
        // ...
    };

### <a name="Rc-factory"></a>C.50: Use a factory function if you need "virtual behavior" during initialization

##### Reason

If the state of a base class object must depend on the state of a derived part of the object, we need to use a virtual function (or equivalent) while minimizing the window of opportunity to misuse an imperfectly constructed object.

##### Note

The return type of the factory should normally be `unique_ptr` by default; if some uses are shared, the caller can `move` the `unique_ptr` into a `shared_ptr`. However, if the factory author knows that all uses of the returned object will be shared uses, return `shared_ptr` and use `make_shared` in the body to save an allocation.

##### Example, bad

    class B {
    public:
        B()
        {
            /* ... */
            f(); // BAD: C.82: Don't call virtual functions in constructors and destructors
            /* ... */
        }

        virtual void f() = 0;
    };

##### Example

    class B {
    protected:
        class Token {};

    public:
        explicit B(Token) { /* ... */ }  // create an imperfectly initialized object
        virtual void f() = 0;

        template<class T>
        static shared_ptr<T> create()    // interface for creating shared objects
        {
            auto p = make_shared<T>(typename T::Token{});
            p->post_initialize();
            return p;
        }

    protected:
        virtual void post_initialize()   // called right after construction
            { /* ... */ f(); /* ... */ } // GOOD: virtual dispatch is safe
    };

    class D : public B {                 // some derived class
    protected:
        class Token {};

    public:
        explicit D(Token) : B{ B::Token{} } {}
        void f() override { /* ...  */ };

    protected:
        template<class T>
        friend shared_ptr<T> B::create();
    };

    shared_ptr<D> p = D::create<D>();  // creating a D object

`make_shared` requires that the constructor is public. By requiring a protected `Token` the constructor cannot be publicly called anymore, so we avoid an incompletely constructed object escaping into the wild.
By providing the factory function `create()`, we make construction (on the free store) convenient.

##### Note

Conventional factory functions allocate on the free store, rather than on the stack or in an enclosing object.

**See also**: [Discussion](#Sd-factory)

### <a name="Rc-delegating"></a>C.51: Use delegating constructors to represent common actions for all constructors of a class

##### Reason

To avoid repetition and accidental differences.

##### Example, bad

    class Date {   // BAD: repetitive
        int d;
        Month m;
        int y;
    public:
        Date(int dd, Month mm, year yy)
            :d{dd}, m{mm}, y{yy}
            { if (!valid(d, m, y)) throw Bad_date{}; }

        Date(int dd, Month mm)
            :d{dd}, m{mm} y{current_year()}
            { if (!valid(d, m, y)) throw Bad_date{}; }
        // ...
    };

The common action gets tedious to write and might accidentally not be common.

##### Example

    class Date2 {
        int d;
        Month m;
        int y;
    public:
        Date2(int dd, Month mm, year yy)
            :d{dd}, m{mm}, y{yy}
            { if (!valid(d, m, y)) throw Bad_date{}; }

        Date2(int dd, Month mm)
            :Date2{dd, mm, current_year()} {}
        // ...
    };

**See also**: If the "repeated action" is a simple initialization, consider [a default member initializer](#Rc-in-class-initializer).

##### Enforcement

(Moderate) Look for similar constructor bodies.

### <a name="Rc-inheriting"></a>C.52: Use inheriting constructors to import constructors into a derived class that does not need further explicit initialization

##### Reason

If you need those constructors for a derived class, re-implementing them is tedious and error-prone.

##### Example

`std::vector` has a lot of tricky constructors, so if I want my own `vector`, I don't want to reimplement them:

    class Rec {
        // ... data and lots of nice constructors ...
    };

    class Oper : public Rec {
        using Rec::Rec;
        // ... no data members ...
        // ... lots of nice utility functions ...
    };

##### Example, bad

    struct Rec2 : public Rec {
        int x;
        using Rec::Rec;
    };

    Rec2 r {"foo", 7};
    int val = r.x;   // uninitialized

##### Enforcement

Make sure that every member of the derived class is initialized.

## <a name="SS-copy"></a>C.copy: Copy and move

Concrete types should generally be copyable, but interfaces in a class hierarchy should not.
Resource handles might or might not be copyable.
Types can be defined to move for logical as well as performance reasons.

### <a name="Rc-copy-assignment"></a>C.60: Make copy assignment non-`virtual`, take the parameter by `const&`, and return by non-`const&`

##### Reason

It is simple and efficient. If you want to optimize for rvalues, provide an overload that takes a `&&` (see [F.18](#Rf-consume)).

##### Example

    class Foo {
    public:
        Foo& operator=(const Foo& x)
        {
            // GOOD: no need to check for self-assignment (other than performance)
            auto tmp = x;
            swap(tmp); // see C.83
            return *this;
        }
        // ...
    };

    Foo a;
    Foo b;
    Foo f();

    a = b;    // assign lvalue: copy
    a = f();  // assign rvalue: potentially move

##### Note

The `swap` implementation technique offers the [strong guarantee](#Abrahams01).

##### Example

But what if you can get significantly better performance by not making a temporary copy? Consider a simple `Vector` intended for a domain where assignment of large, equal-sized `Vector`s is common. In this case, the copy of elements implied by the `swap` implementation technique could cause an order of magnitude increase in cost:

    template<typename T>
    class Vector {
    public:
        Vector& operator=(const Vector&);
        // ...
    private:
        T* elem;
        int sz;
    };

    Vector& Vector::operator=(const Vector& a)
    {
        if (a.sz > sz) {
            // ... use the swap technique, it can't be bettered ...
            return *this;
        }
        // ... copy sz elements from *a.elem to elem ...
        if (a.sz < sz) {
            // ... destroy the surplus elements in *this and adjust size ...
        }
        return *this;
    }

By writing directly to the target elements, we will get only [the basic guarantee](#Abrahams01) rather than the strong guarantee offered by the `swap` technique. Beware of [self-assignment](#Rc-copy-self).

**Alternatives**: If you think you need a `virtual` assignment operator, and understand why that's deeply problematic, don't call it `operator=`. Make it a named function like `virtual void assign(const Foo&)`.
See [copy constructor vs. `clone()`](#Rc-copy-virtual).

##### Enforcement

* (Simple) An assignment operator should not be virtual. Here be dragons!
* (Simple) An assignment operator should return `T&` to enable chaining, not alternatives like `const T&` which interfere with composability and putting objects in containers.
* (Moderate) An assignment operator should (implicitly or explicitly) invoke all base and member assignment operators.
  Look at the destructor to determine if the type has pointer semantics or value semantics.

### <a name="Rc-copy-semantic"></a>C.61: A copy operation should copy

##### Reason

That is the generally assumed semantics. After `x = y`, we should have `x == y`.
After a copy `x` and `y` can be independent objects (value semantics, the way non-pointer built-in types and the standard-library types work) or refer to a shared object (pointer semantics, the way pointers work).

##### Example

    class X {   // OK: value semantics
    public:
        X();
        X(const X&);     // copy X
        void modify();   // change the value of X
        // ...
        ~X() { delete[] p; }
    private:
        T* p;
        int sz;
    };

    bool operator==(const X& a, const X& b)
    {
        return a.sz == b.sz && equal(a.p, a.p + a.sz, b.p, b.p + b.sz);
    }

    X::X(const X& a)
        :p{new T[a.sz]}, sz{a.sz}
    {
        copy(a.p, a.p + sz, p);
    }

    X x;
    X y = x;
    if (x != y) throw Bad{};
    x.modify();
    if (x == y) throw Bad{};   // assume value semantics

##### Example

    class X2 {  // OK: pointer semantics
    public:
        X2();
        X2(const X2&) = default; // shallow copy
        ~X2() = default;
        void modify();          // change the pointed-to value
        // ...
    private:
        T* p;
        int sz;
    };

    bool operator==(const X2& a, const X2& b)
    {
        return a.sz == b.sz && a.p == b.p;
    }

    X2 x;
    X2 y = x;
    if (x != y) throw Bad{};
    x.modify();
    if (x != y) throw Bad{};  // assume pointer semantics

##### Note

Prefer value semantics unless you are building a "smart pointer". Value semantics is the simplest to reason about and what the standard-library facilities expect.

##### Enforcement

(Not enforceable)

### <a name="Rc-copy-self"></a>C.62: Make copy assignment safe for self-assignment

##### Reason

If `x = x` changes the value of `x`, people will be surprised and bad errors will occur (often including leaks).

##### Example

The standard-library containers handle self-assignment elegantly and efficiently:

    std::vector<int> v = {3, 1, 4, 1, 5, 9};
    v = v;
    // the value of v is still {3, 1, 4, 1, 5, 9}

##### Note

The default assignment generated from members that handle self-assignment correctly handles self-assignment.

    struct Bar {
        vector<pair<int, int>> v;
        map<string, int> m;
        string s;
    };

    Bar b;
    // ...
    b = b;   // correct and efficient

##### Note

You can handle self-assignment by explicitly testing for self-assignment, but often it is faster and more elegant to cope without such a test (e.g., [using `swap`](#Rc-swap)).

    class Foo {
        string s;
        int i;
    public:
        Foo& operator=(const Foo& a);
        // ...
    };

    Foo& Foo::operator=(const Foo& a)   // OK, but there is a cost
    {
        if (this == &a) return *this;
        s = a.s;
        i = a.i;
        return *this;
    }

This is obviously safe and apparently efficient.
However, what if we do one self-assignment per million assignments?
That's about a million redundant tests (but since the answer is essentially always the same, the computer's branch predictor will guess right essentially every time).
Consider:

    Foo& Foo::operator=(const Foo& a)   // simpler, and probably much better
    {
        s = a.s;
        i = a.i;
        return *this;
    }

`std::string` is safe for self-assignment and so are `int`. All the cost is carried by the (rare) case of self-assignment.

##### Enforcement

(Simple) Assignment operators should not contain the pattern `if (this == &a) return *this;` ???

### <a name="Rc-move-assignment"></a>C.63: Make move assignment non-`virtual`, take the parameter by `&&`, and return by non-`const&`

##### Reason

It is simple and efficient.

**See**: [The rule for copy-assignment](#Rc-copy-assignment).

##### Enforcement

Equivalent to what is done for [copy-assignment](#Rc-copy-assignment).

* (Simple) An assignment operator should not be virtual. Here be dragons!
* (Simple) An assignment operator should return `T&` to enable chaining, not alternatives like `const T&` which interfere with composability and putting objects in containers.
* (Moderate) A move assignment operator should (implicitly or explicitly) invoke all base and member move assignment operators.

### <a name="Rc-move-semantic"></a>C.64: A move operation should move and leave its source in a valid state

##### Reason

That is the generally assumed semantics.
After `y = std::move(x)` the value of `y` should be the value `x` had and `x` should be in a valid state.

##### Example

    class X {   // OK: value semantics
    public:
        X();
        X(X&& a) noexcept;  // move X
        X& operator=(X&& a) noexcept; // move-assign X
        void modify();     // change the value of X
        // ...
        ~X() { delete[] p; }
    private:
        T* p;
        int sz;
    };

    X::X(X&& a) noexcept
        :p{a.p}, sz{a.sz}  // steal representation
    {
        a.p = nullptr;     // set to "empty"
        a.sz = 0;
    }

    void use()
    {
        X x{};
        // ...
        X y = std::move(x);
        x = X{};   // OK
    } // OK: x can be destroyed

##### Note

Ideally, that moved-from should be the default value of the type.
Ensure that unless there is an exceptionally good reason not to.
However, not all types have a default value and for some types establishing the default value can be expensive.
The standard requires only that the moved-from object can be destroyed.
Often, we can easily and cheaply do better: The standard library assumes that it is possible to assign to a moved-from object.
Always leave the moved-from object in some (necessarily specified) valid state.

##### Note

Unless there is an exceptionally strong reason not to, make `x = std::move(y); y = z;` work with the conventional semantics.

##### Enforcement

(Not enforceable) Look for assignments to members in the move operation. If there is a default constructor, compare those assignments to the initializations in the default constructor.

### <a name="Rc-move-self"></a>C.65: Make move assignment safe for self-assignment

##### Reason

If `x = x` changes the value of `x`, people will be surprised and bad errors can occur. However, people don't usually directly write a self-assignment that turn into a move, but it can occur. However, `std::swap` is implemented using move operations so if you accidentally do `swap(a, b)` where `a` and `b` refer to the same object, failing to handle self-move could be a serious and subtle error.

##### Example

    class Foo {
        string s;
        int i;
    public:
        Foo& operator=(Foo&& a) noexcept;
        // ...
    };

    Foo& Foo::operator=(Foo&& a) noexcept  // OK, but there is a cost
    {
        if (this == &a) return *this;  // this line is redundant
        s = std::move(a.s);
        i = a.i;
        return *this;
    }

The one-in-a-million argument against `if (this == &a) return *this;` tests from the discussion of [self-assignment](#Rc-copy-self) is even more relevant for self-move.

##### Note

There is no known general way of avoiding an `if (this == &a) return *this;` test for a move assignment and still get a correct answer (i.e., after `x = x` the value of `x` is unchanged).

##### Note

The ISO standard guarantees only a "valid but unspecified" state for the standard-library containers. Apparently this has not been a problem in about 10 years of experimental and production use. Please contact the editors if you find a counter example. The rule here is more caution and insists on complete safety.

##### Example

Here is a way to move a pointer without a test (imagine it as code in the implementation a move assignment):

    // move from other.ptr to this->ptr
    T* temp = other.ptr;
    other.ptr = nullptr;
    delete ptr; // in self-move, this->ptr is also null; delete is a no-op
    ptr = temp; // in self-move, the original ptr is restored

##### Enforcement

* (Moderate) In the case of self-assignment, a move assignment operator should not leave the object holding pointer members that have been `delete`d or set to `nullptr`.
* (Not enforceable) Look at the use of standard-library container types (incl. `string`) and consider them safe for ordinary (not life-critical) uses.

### <a name="Rc-move-noexcept"></a>C.66: Make move operations `noexcept`

##### Reason

A throwing move violates most people's reasonable assumptions.
A non-throwing move will be used more efficiently by standard-library and language facilities.

##### Example

    template<typename T>
    class Vector {
    public:
        Vector(Vector&& a) noexcept :elem{a.elem}, sz{a.sz} { a.elem = nullptr; a.sz = 0; }
        Vector& operator=(Vector&& a) noexcept {
            if (&a != this) {
                delete elem;
                elem = a.elem; a.elem = nullptr;
                sz   = a.sz;   a.sz   = 0;
            }
            return *this;
        }
        // ...
    private:
        T* elem;
        int sz;
    };

These operations do not throw.

##### Example, bad

    template<typename T>
    class Vector2 {
    public:
        Vector2(Vector2&& a) noexcept { *this = a; }             // just use the copy
        Vector2& operator=(Vector2&& a) noexcept { *this = a; }  // just use the copy
        // ...
    private:
        T* elem;
        int sz;
    };

This `Vector2` is not just inefficient, but since a vector copy requires allocation, it can throw.

##### Enforcement

(Simple) A move operation should be marked `noexcept`.

### <a name="Rc-copy-virtual"></a>C.67: A polymorphic class should suppress public copy/move

##### Reason

A *polymorphic class* is a class that defines or inherits at least one virtual function. It is likely that it will be used as a base class for other derived classes with polymorphic behavior. If it is accidentally passed by value, with the implicitly generated copy constructor and assignment, we risk slicing: only the base portion of a derived object will be copied, and the polymorphic behavior will be corrupted.

If the class has no data, `=delete` the copy/move functions. Otherwise, make them protected.

##### Example, bad

    class B { // BAD: polymorphic base class doesn't suppress copying
    public:
        virtual char m() { return 'B'; }
        // ... nothing about copy operations, so uses default ...
    };

    class D : public B {
    public:
        char m() override { return 'D'; }
        // ...
    };

    void f(B& b)
    {
        auto b2 = b; // oops, slices the object; b2.m() will return 'B'
    }

    D d;
    f(d);

##### Example

    class B { // GOOD: polymorphic class suppresses copying
    public:
        B() = default;
        B(const B&) = delete;
        B& operator=(const B&) = delete;
        virtual char m() { return 'B'; }
        // ...
    };

    class D : public B {
    public:
        char m() override { return 'D'; }
        // ...
    };

    void f(B& b)
    {
        auto b2 = b; // ok, compiler will detect inadvertent copying, and protest
    }

    D d;
    f(d);

##### Note

If you need to create deep copies of polymorphic objects, use `clone()` functions: see [C.130](#Rh-copy).

##### Exception

Classes that represent exception objects need both to be polymorphic and copy-constructible.

##### Enforcement

* Flag a polymorphic class with a public copy operation.
* Flag an assignment of polymorphic class objects.

## C.other: Other default operation rules

In addition to the operations for which the language offers default implementations,
there are a few operations that are so foundational that specific rules for their definition are needed:
comparisons, `swap`, and `hash`.

### <a name="Rc-eqdefault"></a>C.80: Use `=default` if you have to be explicit about using the default semantics

##### Reason

The compiler is more likely to get the default semantics right and you cannot implement these functions better than the compiler.

##### Example

    class Tracer {
        string message;
    public:
        Tracer(const string& m) : message{m} { cerr << "entering " << message << '\n'; }
        ~Tracer() { cerr << "exiting " << message << '\n'; }

        Tracer(const Tracer&) = default;
        Tracer& operator=(const Tracer&) = default;
        Tracer(Tracer&&) noexcept = default;
        Tracer& operator=(Tracer&&) noexcept = default;
    };

Because we defined the destructor, we must define the copy and move operations. The `= default` is the best and simplest way of doing that.

##### Example, bad

    class Tracer2 {
        string message;
    public:
        Tracer2(const string& m) : message{m} { cerr << "entering " << message << '\n'; }
        ~Tracer2() { cerr << "exiting " << message << '\n'; }

        Tracer2(const Tracer2& a) : message{a.message} {}
        Tracer2& operator=(const Tracer2& a) { message = a.message; return *this; }
        Tracer2(Tracer2&& a) noexcept :message{a.message} {}
        Tracer2& operator=(Tracer2&& a) noexcept { message = a.message; return *this; }
    };

Writing out the bodies of the copy and move operations is verbose, tedious, and error-prone. A compiler does it better.

##### Enforcement

(Moderate) The body of a user-defined operation should not have the same semantics as the compiler-generated version, because that would be redundant.

### <a name="Rc-delete"></a>C.81: Use `=delete` when you want to disable default behavior (without wanting an alternative)

##### Reason

In a few cases, a default operation is not desirable.

##### Example

    class Immortal {
    public:
        ~Immortal() = delete;   // do not allow destruction
        // ...
    };

    void use()
    {
        Immortal ugh;   // error: ugh cannot be destroyed
        Immortal* p = new Immortal{};
        delete p;       // error: cannot destroy *p
    }

##### Example

A `unique_ptr` can be moved, but not copied. To achieve that its copy operations are deleted. To avoid copying it is necessary to `=delete` its copy operations from lvalues:

    template<class T, class D = default_delete<T>> class unique_ptr {
    public:
        // ...
        constexpr unique_ptr() noexcept;
        explicit unique_ptr(pointer p) noexcept;
        // ...
        unique_ptr(unique_ptr&& u) noexcept;   // move constructor
        // ...
        unique_ptr(const unique_ptr&) = delete; // disable copy from lvalue
        // ...
    };

    unique_ptr<int> make();   // make "something" and return it by moving

    void f()
    {
        unique_ptr<int> pi {};
        auto pi2 {pi};      // error: no move constructor from lvalue
        auto pi3 {make()};  // OK, move: the result of make() is an rvalue
    }

Note that deleted functions should be public.

##### Enforcement

The elimination of a default operation is (should be) based on the desired semantics of the class. Consider such classes suspect, but maintain a "positive list" of classes where a human has asserted that the semantics is correct.

### <a name="Rc-ctor-virtual"></a>C.82: Don't call virtual functions in constructors and destructors

##### Reason

The function called will be that of the object constructed so far, rather than a possibly overriding function in a derived class.
This can be most confusing.
Worse, a direct or indirect call to an unimplemented pure virtual function from a constructor or destructor results in undefined behavior.

##### Example, bad

    class Base {
    public:
        virtual void f() = 0;   // not implemented
        virtual void g();       // implemented with Base version
        virtual void h();       // implemented with Base version
        virtual ~Base();        // implemented with Base version
    };

    class Derived : public Base {
    public:
        void g() override;   // provide Derived implementation
        void h() final;      // provide Derived implementation

        Derived()
        {
            // BAD: attempt to call an unimplemented virtual function
            f();

            // BAD: will call Derived::g, not dispatch further virtually
            g();

            // GOOD: explicitly state intent to call only the visible version
            Derived::g();

            // ok, no qualification needed, h is final
            h();
        }
    };

Note that calling a specific explicitly qualified function is not a virtual call even if the function is `virtual`.

**See also** [factory functions](#Rc-factory) for how to achieve the effect of a call to a derived class function without risking undefined behavior.

##### Note

There is nothing inherently wrong with calling virtual functions from constructors and destructors.
The semantics of such calls is type safe.
However, experience shows that such calls are rarely needed, easily confuse maintainers, and become a source of errors when used by novices.

##### Enforcement

* Flag calls of virtual functions from constructors and destructors.

### <a name="Rc-swap"></a>C.83: For value-like types, consider providing a `noexcept` swap function

##### Reason

A `swap` can be handy for implementing a number of idioms, from smoothly moving objects around to implementing assignment easily to providing a guaranteed commit function that enables strongly error-safe calling code. Consider using swap to implement copy assignment in terms of copy construction. See also [destructors, deallocation, and swap must never fail](#Re-never-fail).

##### Example, good

    class Foo {
    public:
        void swap(Foo& rhs) noexcept
        {
            m1.swap(rhs.m1);
            std::swap(m2, rhs.m2);
        }
    private:
        Bar m1;
        int m2;
    };

Providing a non-member `swap` function in the same namespace as your type for callers' convenience.

    void swap(Foo& a, Foo& b)
    {
        a.swap(b);
    }

##### Enforcement

* Non-trivially copyable types should provide a member swap or a free swap overload.
* (Simple) When a class has a `swap` member function, it should be declared `noexcept`.

### <a name="Rc-swap-fail"></a>C.84: A `swap` function must not fail

##### Reason

 `swap` is widely used in ways that are assumed never to fail and programs cannot easily be written to work correctly in the presence of a failing `swap`. The standard-library containers and algorithms will not work correctly if a swap of an element type fails.

##### Example, bad

    void swap(My_vector& x, My_vector& y)
    {
        auto tmp = x;   // copy elements
        x = y;
        y = tmp;
    }

This is not just slow, but if a memory allocation occurs for the elements in `tmp`, this `swap` could throw and would make STL algorithms fail if used with them.

##### Enforcement

(Simple) When a class has a `swap` member function, it should be declared `noexcept`.

### <a name="Rc-swap-noexcept"></a>C.85: Make `swap` `noexcept`

##### Reason

 [A `swap` must not fail](#Rc-swap-fail).
If a `swap` tries to exit with an exception, it's a bad design error and the program had better terminate.

##### Enforcement

(Simple) When a class has a `swap` member function, it should be declared `noexcept`.

### <a name="Rc-eq"></a>C.86: Make `==` symmetric with respect to operand types and `noexcept`

##### Reason

Asymmetric treatment of operands is surprising and a source of errors where conversions are possible.
`==` is a fundamental operation and programmers should be able to use it without fear of failure.

##### Example

    struct X {
        string name;
        int number;
    };

    bool operator==(const X& a, const X& b) noexcept {
        return a.name == b.name && a.number == b.number;
    }

##### Example, bad

    class B {
        string name;
        int number;
        bool operator==(const B& a) const {
            return name == a.name && number == a.number;
        }
        // ...
    };

`B`'s comparison accepts conversions for its second operand, but not its first.

##### Note

If a class has a failure state, like `double`'s `NaN`, there is a temptation to make a comparison against the failure state throw.
The alternative is to make two failure states compare equal and any valid state compare false against the failure state.

##### Note

This rule applies to all the usual comparison operators: `!=`, `<`, `<=`, `>`, and `>=`.

##### Enforcement

* Flag an `operator==()` for which the argument types differ; same for other comparison operators: `!=`, `<`, `<=`, `>`, and `>=`.
* Flag member `operator==()`s; same for other comparison operators: `!=`, `<`, `<=`, `>`, and `>=`.

### <a name="Rc-eq-base"></a>C.87: Beware of `==` on base classes

##### Reason

It is really hard to write a foolproof and useful `==` for a hierarchy.

##### Example, bad

    class B {
        string name;
        int number;
    public:
        virtual bool operator==(const B& a) const
        {
             return name == a.name && number == a.number;
        }
        // ...
    };

`B`'s comparison accepts conversions for its second operand, but not its first.

    class D : public B {
        char character;
    public:
        virtual bool operator==(const D& a) const
        {
            return B::operator==(a) && character == a.character;
        }
        // ...
    };

    B b = ...
    D d = ...
    b == d;    // compares name and number, ignores d's character
    d == b;    // compares name and number, ignores d's character
    D d2;
    d == d2;   // compares name, number, and character
    B& b2 = d2;
    b2 == d;   // compares name and number, ignores d2's and d's character

Of course there are ways of making `==` work in a hierarchy, but the naive approaches do not scale

##### Note

This rule applies to all the usual comparison operators: `!=`, `<`, `<=`, `>`, `>=`, and `<=>`.

##### Enforcement

* Flag a virtual `operator==()`; same for other comparison operators: `!=`, `<`, `<=`, `>`, `>=`, and `<=>`.

### <a name="Rc-hash"></a>C.89: Make a `hash` `noexcept`

##### Reason

Users of hashed containers use hash indirectly and don't expect simple access to throw.
It's a standard-library requirement.

##### Example, bad

    template<>
    struct hash<My_type> {  // thoroughly bad hash specialization
        using result_type = size_t;
        using argument_type = My_type;

        size_t operator()(const My_type & x) const
        {
            size_t xs = x.s.size();
            if (xs < 4) throw Bad_My_type{};    // "Nobody expects the Spanish inquisition!"
            return hash<size_t>()(x.s.size()) ^ trim(x.s);
        }
    };

    int main()
    {
        unordered_map<My_type, int> m;
        My_type mt{ "asdfg" };
        m[mt] = 7;
        cout << m[My_type{ "asdfg" }] << '\n';
    }

If you have to define a `hash` specialization, try simply to let it combine standard-library `hash` specializations with `^` (xor).
That tends to work better than "cleverness" for non-specialists.

##### Enforcement

* Flag throwing `hash`es.

### <a name="Rc-memset"></a>C.90: Rely on constructors and assignment operators, not `memset` and `memcpy`

##### Reason

The standard C++ mechanism to construct an instance of a type is to call its constructor. As specified in guideline [C.41](#Rc-complete): a constructor should create a fully initialized object. No additional initialization, such as by `memcpy`, should be required.
A type will provide a copy constructor and/or copy assignment operator to appropriately make a copy of the class, preserving the type's invariants.  Using memcpy to copy a non-trivially copyable type has undefined behavior.  Frequently this results in slicing, or data corruption.

##### Example, good

    struct base {
        virtual void update() = 0;
        std::shared_ptr<int> sp;
    };

    struct derived : public base {
        void update() override {}
    };

##### Example, bad

    void init(derived& a)
    {
        memset(&a, 0, sizeof(derived));
    }

This is type-unsafe and overwrites the vtable.

##### Example, bad

    void copy(derived& a, derived& b)
    {
        memcpy(&a, &b, sizeof(derived));
    }

This is also type-unsafe and overwrites the vtable.

##### Enforcement

* Flag passing a non-trivially-copyable type to `memset` or `memcpy`.

## <a name="SS-containers"></a>C.con: Containers and other resource handles

A container is an object holding a sequence of objects of some type; `std::vector` is the archetypical container.
A resource handle is a class that owns a resource; `std::vector` is the typical resource handle; its resource is its sequence of elements.

Summary of container rules:

* [C.100: Follow the STL when defining a container](#Rcon-stl)
* [C.101: Give a container value semantics](#Rcon-val)
* [C.102: Give a container move operations](#Rcon-move)
* [C.103: Give a container an initializer list constructor](#Rcon-init)
* [C.104: Give a container a default constructor that sets it to empty](#Rcon-empty)
* ???
* [C.109: If a resource handle has pointer semantics, provide `*` and `->`](#Rcon-ptr)

**See also**: [Resources](#S-resource)


### <a name="Rcon-stl"></a>C.100: Follow the STL when defining a container

##### Reason

The STL containers are familiar to most C++ programmers and a fundamentally sound design.

##### Note

There are of course other fundamentally sound design styles and sometimes reasons to depart from
the style of the standard library, but in the absence of a solid reason to differ, it is simpler
and easier for both implementers and users to follow the standard.

In particular, `std::vector` and `std::map` provide useful relatively simple models.

##### Example

    // simplified (e.g., no allocators):

    template<typename T>
    class Sorted_vector {
        using value_type = T;
        // ... iterator types ...

        Sorted_vector() = default;
        Sorted_vector(initializer_list<T>);    // initializer-list constructor: sort and store
        Sorted_vector(const Sorted_vector&) = default;
        Sorted_vector(Sorted_vector&&) noexcept = default;
        Sorted_vector& operator=(const Sorted_vector&) = default;     // copy assignment
        Sorted_vector& operator=(Sorted_vector&&) noexcept = default; // move assignment
        ~Sorted_vector() = default;

        Sorted_vector(const std::vector<T>& v);   // store and sort
        Sorted_vector(std::vector<T>&& v);        // sort and "steal representation"

        const T& operator[](int i) const { return rep[i]; }
        // no non-const direct access to preserve order

        void push_back(const T&);   // insert in the right place (not necessarily at back)
        void push_back(T&&);        // insert in the right place (not necessarily at back)

        // ... cbegin(), cend() ...
    private:
        std::vector<T> rep;  // use a std::vector to hold elements
    };

    template<typename T> bool operator==(const Sorted_vector<T>&, const Sorted_vector<T>&);
    template<typename T> bool operator!=(const Sorted_vector<T>&, const Sorted_vector<T>&);
    // ...

Here, the STL style is followed, but incompletely.
That's not uncommon.
Provide only as much functionality as makes sense for a specific container.
The key is to define the conventional constructors, assignments, destructors, and iterators
(as meaningful for the specific container) with their conventional semantics.
From that base, the container can be expanded as needed.
Here, special constructors from `std::vector` were added.

##### Enforcement

???

### <a name="Rcon-val"></a>C.101: Give a container value semantics

##### Reason

Regular objects are simpler to think and reason about than irregular ones.
Familiarity.

##### Note

If meaningful, make a container `Regular` (the concept).
In particular, ensure that an object compares equal to its copy.

##### Example

    void f(const Sorted_vector<string>& v)
    {
        Sorted_vector<string> v2 {v};
        if (v != v2)
            cout << "Behavior against reason and logic.\n";
        // ...
    }

##### Enforcement

???

### <a name="Rcon-move"></a>C.102: Give a container move operations

##### Reason

Containers tend to get large; without a move constructor and a copy constructor an object can be
expensive to move around, thus tempting people to pass pointers to it around and getting into
resource management problems.

##### Example

    Sorted_vector<int> read_sorted(istream& is)
    {
        vector<int> v;
        cin >> v;   // assume we have a read operation for vectors
        Sorted_vector<int> sv = v;  // sorts
        return sv;
    }

A user can reasonably assume that returning a standard-like container is cheap.

##### Enforcement

???

### <a name="Rcon-init"></a>C.103: Give a container an initializer list constructor

##### Reason

People expect to be able to initialize a container with a set of values.
Familiarity.

##### Example

    Sorted_vector<int> sv {1, 3, -1, 7, 0, 0}; // Sorted_vector sorts elements as needed

##### Enforcement

???

### <a name="Rcon-empty"></a>C.104: Give a container a default constructor that sets it to empty

##### Reason

To make it `Regular`.

##### Example

    vector<Sorted_sequence<string>> vs(100);    // 100 Sorted_sequences each with the value ""

##### Enforcement

???

### <a name="Rcon-ptr"></a>C.109: If a resource handle has pointer semantics, provide `*` and `->`

##### Reason

That's what is expected from pointers.
Familiarity.

##### Example

    ???

##### Enforcement

???

## <a name="SS-lambdas"></a>C.lambdas: Function objects and lambdas

A function object is an object supplying an overloaded `()` so that you can call it.
A lambda expression (colloquially often shortened to "a lambda") is a notation for generating a function object.
Function objects should be cheap to copy (and therefore [passed by value](#Rf-in)).

Summary:

* [F.10: If an operation can be reused, give it a name](#Rf-name)
* [F.11: Use an unnamed lambda if you need a simple function object in one place only](#Rf-lambda)
* [F.50: Use a lambda when a function won't do (to capture local variables, or to write a local function)](#Rf-capture-vs-overload)
* [F.52: Prefer capturing by reference in lambdas that will be used locally, including passed to algorithms](#Rf-reference-capture)
* [F.53: Avoid capturing by reference in lambdas that will be used non-locally, including returned, stored on the heap, or passed to another thread](#Rf-value-capture)
* [ES.28: Use lambdas for complex initialization, especially of `const` variables](#Res-lambda-init)

## <a name="SS-hier"></a>C.hier: Class hierarchies (OOP)

A class hierarchy is constructed to represent a set of hierarchically organized concepts (only).
Typically base classes act as interfaces.
There are two major uses for hierarchies, often named implementation inheritance and interface inheritance.

Class hierarchy rule summary:

* [C.120: Use class hierarchies to represent concepts with inherent hierarchical structure (only)](#Rh-domain)
* [C.121: If a base class is used as an interface, make it a pure abstract class](#Rh-abstract)
* [C.122: Use abstract classes as interfaces when complete separation of interface and implementation is needed](#Rh-separation)

Designing rules for classes in a hierarchy summary:

* [C.126: An abstract class typically doesn't need a user-written constructor](#Rh-abstract-ctor)
* [C.127: A class with a virtual function should have a virtual or protected destructor](#Rh-dtor)
* [C.128: Virtual functions should specify exactly one of `virtual`, `override`, or `final`](#Rh-override)
* [C.129: When designing a class hierarchy, distinguish between implementation inheritance and interface inheritance](#Rh-kind)
* [C.130: For making deep copies of polymorphic classes prefer a virtual `clone` function instead of public copy construction/assignment](#Rh-copy)
* [C.131: Avoid trivial getters and setters](#Rh-get)
* [C.132: Don't make a function `virtual` without reason](#Rh-virtual)
* [C.133: Avoid `protected` data](#Rh-protected)
* [C.134: Ensure all non-`const` data members have the same access level](#Rh-public)
* [C.135: Use multiple inheritance to represent multiple distinct interfaces](#Rh-mi-interface)
* [C.136: Use multiple inheritance to represent the union of implementation attributes](#Rh-mi-implementation)
* [C.137: Use `virtual` bases to avoid overly general base classes](#Rh-vbase)
* [C.138: Create an overload set for a derived class and its bases with `using`](#Rh-using)
* [C.139: Use `final` on classes sparingly](#Rh-final)
* [C.140: Do not provide different default arguments for a virtual function and an overrider](#Rh-virtual-default-arg)

Accessing objects in a hierarchy rule summary:

* [C.145: Access polymorphic objects through pointers and references](#Rh-poly)
* [C.146: Use `dynamic_cast` where class hierarchy navigation is unavoidable](#Rh-dynamic_cast)
* [C.147: Use `dynamic_cast` to a reference type when failure to find the required class is considered an error](#Rh-ref-cast)
* [C.148: Use `dynamic_cast` to a pointer type when failure to find the required class is considered a valid alternative](#Rh-ptr-cast)
* [C.149: Use `unique_ptr` or `shared_ptr` to avoid forgetting to `delete` objects created using `new`](#Rh-smart)
* [C.150: Use `make_unique()` to construct objects owned by `unique_ptr`s](#Rh-make_unique)
* [C.151: Use `make_shared()` to construct objects owned by `shared_ptr`s](#Rh-make_shared)
* [C.152: Never assign a pointer to an array of derived class objects to a pointer to its base](#Rh-array)
* [C.153: Prefer virtual function to casting](#Rh-use-virtual)

### <a name="Rh-domain"></a>C.120: Use class hierarchies to represent concepts with inherent hierarchical structure (only)

##### Reason

Direct representation of ideas in code eases comprehension and maintenance. Make sure the idea represented in the base class exactly matches all derived types and there is not a better way to express it than using the tight coupling of inheritance.

Do *not* use inheritance when simply having a data member will do. Usually this means that the derived type needs to override a base virtual function or needs access to a protected member.

##### Example

    class DrawableUIElement {
    public:
        virtual void render() const = 0;
        // ...
    };

    class AbstractButton : public DrawableUIElement {
    public:
        virtual void onClick() = 0;
        // ...
    };

    class PushButton : public AbstractButton {
        void render() const override;
        void onClick() override;
        // ...
    };

    class Checkbox : public AbstractButton {
    // ...
    };

##### Example, bad

Do *not* represent non-hierarchical domain concepts as class hierarchies.

    template<typename T>
    class Container {
    public:
        // list operations:
        virtual T& get() = 0;
        virtual void put(T&) = 0;
        virtual void insert(Position) = 0;
        // ...
        // vector operations:
        virtual T& operator[](int) = 0;
        virtual void sort() = 0;
        // ...
        // tree operations:
        virtual void balance() = 0;
        // ...
    };

Here most overriding classes cannot implement most of the functions required in the interface well.
Thus the base class becomes an implementation burden.
Furthermore, the user of `Container` cannot rely on the member functions actually performing meaningful operations reasonably efficiently;
it might throw an exception instead.
Thus users have to resort to run-time checking and/or
not using this (over)general interface in favor of a particular interface found by a run-time type inquiry (e.g., a `dynamic_cast`).

##### Enforcement

* Look for classes with lots of members that do nothing but throw.
* Flag every use of a non-public base class `B` where the derived class `D` does not override a virtual function or access a protected member in `B`, and `B` is not one of the following: empty, a template parameter or parameter pack of `D`, a class template specialized with `D`.

### <a name="Rh-abstract"></a>C.121: If a base class is used as an interface, make it a pure abstract class

##### Reason

A class is more stable (less brittle) if it does not contain data.
Interfaces should normally be composed entirely of public pure virtual functions and a default/empty virtual destructor.

##### Example

    class My_interface {
    public:
        // ...only pure virtual functions here ...
        virtual ~My_interface() {}   // or =default
    };

##### Example, bad

    class Goof {
    public:
        // ...only pure virtual functions here ...
        // no virtual destructor
    };

    class Derived : public Goof {
        string s;
        // ...
    };

    void use()
    {
        unique_ptr<Goof> p {new Derived{"here we go"}};
        f(p.get()); // use Derived through the Goof interface
        g(p.get()); // use Derived through the Goof interface
    } // leak

The `Derived` is `delete`d through its `Goof` interface, so its `string` is leaked.
Give `Goof` a virtual destructor and all is well.


##### Enforcement

* Warn on any class that contains data members and also has an overridable (non-`final`) virtual function that wasn't inherited from a base class.

### <a name="Rh-separation"></a>C.122: Use abstract classes as interfaces when complete separation of interface and implementation is needed

##### Reason

Such as on an ABI (link) boundary.

##### Example

    struct Device {
        virtual ~Device() = default;
        virtual void write(span<const char> outbuf) = 0;
        virtual void read(span<char> inbuf) = 0;
    };

    class D1 : public Device {
        // ... data ...

        void write(span<const char> outbuf) override;
        void read(span<char> inbuf) override;
    };

    class D2 : public Device {
        // ... different data ...

        void write(span<const char> outbuf) override;
        void read(span<char> inbuf) override;
    };

A user can now use `D1`s and `D2`s interchangeably through the interface provided by `Device`.
Furthermore, we can update `D1` and `D2` in ways that are not binary compatible with older versions as long as all access goes through `Device`.

##### Enforcement

    ???

## C.hierclass: Designing classes in a hierarchy:

### <a name="Rh-abstract-ctor"></a>C.126: An abstract class typically doesn't need a user-written constructor

##### Reason

An abstract class typically does not have any data for a constructor to initialize.

##### Example

    class Shape {
    public:
        // no user-written constructor needed in abstract base class
        virtual Point center() const = 0;    // pure virtual
        virtual void move(Point to) = 0;
        // ... more pure virtual functions...
        virtual ~Shape() {}                 // destructor
    };

    class Circle : public Shape {
    public:
        Circle(Point p, int rad);           // constructor in derived class
        Point center() const override { return x; }
    };

##### Exception

* A base class constructor that does work, such as registering an object somewhere, might need a constructor.
* In extremely rare cases, you might find it reasonable for an abstract class to have a bit of data shared by all derived classes
  (e.g., use statistics data, debug information, etc.); such classes tend to have constructors. But be warned: Such classes also tend to be prone to requiring virtual inheritance.

##### Enforcement

Flag abstract classes with constructors.

### <a name="Rh-dtor"></a>C.127: A class with a virtual function should have a virtual or protected destructor

##### Reason

A class with a virtual function is usually (and in general) used via a pointer to base. Usually, the last user has to call delete on a pointer to base, often via a smart pointer to base, so the destructor should be public and virtual. Less commonly, if deletion through a pointer to base is not intended to be supported, the destructor should be protected and non-virtual; see [C.35](#Rc-dtor-virtual).

##### Example, bad

    struct B {
        virtual int f() = 0;
        // ... no user-written destructor, defaults to public non-virtual ...
    };

    // bad: derived from a class without a virtual destructor
    struct D : B {
        string s {"default"};
        // ...
    };

    void use()
    {
        unique_ptr<B> p = make_unique<D>();
        // ...
    } // undefined behavior, might call B::~B only and leak the string

##### Note

There are people who don't follow this rule because they plan to use a class only through a `shared_ptr`: `std::shared_ptr<B> p = std::make_shared<D>(args);` Here, the shared pointer will take care of deletion, so no leak will occur from an inappropriate `delete` of the base. People who do this consistently can get a false positive, but the rule is important -- what if one was allocated using `make_unique`? It's not safe unless the author of `B` ensures that it can never be misused, such as by making all constructors private and providing a factory function to enforce the allocation with `make_shared`.

##### Enforcement

* A class with any virtual functions should have a destructor that is either public and virtual or else protected and non-virtual.
* Flag `delete` of a class with a virtual function but no virtual destructor.

### <a name="Rh-override"></a>C.128: Virtual functions should specify exactly one of `virtual`, `override`, or `final`

##### Reason

Readability.
Detection of mistakes.
Writing explicit `virtual`, `override`, or `final` is self-documenting and enables the compiler to catch mismatch of types and/or names between base and derived classes. However, writing more than one of these three is both redundant and a potential source of errors.

It's simple and clear:

* `virtual` means exactly and only "this is a new virtual function."
* `override` means exactly and only "this is a non-final overrider."
* `final` means exactly and only "this is a final overrider."

##### Example, bad

    struct B {
        void f1(int);
        virtual void f2(int) const;
        virtual void f3(int);
        // ...
    };

    struct D : B {
        void f1(int);        // bad (hope for a warning): D::f1() hides B::f1()
        void f2(int) const;  // bad (but conventional and valid): no explicit override
        void f3(double);     // bad (hope for a warning): D::f3() hides B::f3()
        // ...
    };

##### Example, good

    struct Better : B {
        void f1(int) override;        // error (caught): Better::f1() hides B::f1()
        void f2(int) const override;
        void f3(double) override;     // error (caught): Better::f3() hides B::f3()
        // ...
    };

#### Discussion

We want to eliminate two particular classes of errors:

* **implicit virtual**: the programmer intended the function to be implicitly virtual and it is (but readers of the code can't tell); or the programmer intended the function to be implicitly virtual but it isn't (e.g., because of a subtle parameter list mismatch); or the programmer did not intend the function to be virtual but it is (because it happens to have the same signature as a virtual in the base class)
* **implicit override**: the programmer intended the function to be implicitly an overrider and it is (but readers of the code can't tell); or the programmer intended the function to be implicitly an overrider but it isn't (e.g., because of a subtle parameter list mismatch); or the programmer did not intend the function to be an overrider but it is (because it happens to have the same signature as a virtual in the base class -- note this problem arises whether or not the function is explicitly declared virtual, because the programmer might have intended to create either a new virtual function or a new non-virtual function)

Note: On a class defined as `final`, it doesn't matter whether you put `override` or `final` on an individual virtual function.

Note: Use `final` on functions sparingly. It does not necessarily lead to optimization, and it precludes further overriding.

##### Enforcement

* Compare virtual function names in base and derived classes and flag uses of the same name that does not override.
* Flag overrides with neither `override` nor `final`.
* Flag function declarations that use more than one of `virtual`, `override`, and `final`.

### <a name="Rh-kind"></a>C.129: When designing a class hierarchy, distinguish between implementation inheritance and interface inheritance

##### Reason

Implementation details in an interface make the interface brittle;
that is, make its users vulnerable to having to recompile after changes in the implementation.
Data in a base class increases the complexity of implementing the base and can lead to replication of code.

##### Note

Definition:

* interface inheritance is the use of inheritance to separate users from implementations,
in particular to allow derived classes to be added and changed without affecting the users of base classes.
* implementation inheritance is the use of inheritance to simplify implementation of new facilities
by making useful operations available for implementers of related new operations (sometimes called "programming by difference").

A pure interface class is simply a set of pure virtual functions; see [I.25](#Ri-abstract).

In early OOP (e.g., in the 1980s and 1990s), implementation inheritance and interface inheritance were often mixed
and bad habits die hard.
Even now, mixtures are not uncommon in old code bases and in old-style teaching material.

The importance of keeping the two kinds of inheritance increases

* with the size of a hierarchy (e.g., dozens of derived classes),
* with the length of time the hierarchy is used (e.g., decades), and
* with the number of distinct organizations in which a hierarchy is used
(e.g., it can be difficult to distribute an update to a base class)


##### Example, bad

    class Shape {   // BAD, mixed interface and implementation
    public:
        Shape();
        Shape(Point ce = {0, 0}, Color co = none): cent{ce}, col {co} { /* ... */}

        Point center() const { return cent; }
        Color color() const { return col; }

        virtual void rotate(int) = 0;
        virtual void move(Point p) { cent = p; redraw(); }

        virtual void redraw();

        // ...
    private:
        Point cent;
        Color col;
    };

    class Circle : public Shape {
    public:
        Circle(Point c, int r) : Shape{c}, rad{r} { /* ... */ }

        // ...
    private:
        int rad;
    };

    class Triangle : public Shape {
    public:
        Triangle(Point p1, Point p2, Point p3); // calculate center
        // ...
    };

Problems:

* As the hierarchy grows and more data is added to `Shape`, the constructors get harder to write and maintain.
* Why calculate the center for the `Triangle`? we might never use it.
* Add a data member to `Shape` (e.g., drawing style or canvas)
and all classes derived from `Shape` and all code using `Shape` will need to be reviewed, possibly changed, and probably recompiled.

The implementation of `Shape::move()` is an example of implementation inheritance:
we have defined `move()` once and for all, for all derived classes.
The more code there is in such base class member function implementations and the more data is shared by placing it in the base,
the more benefits we gain - and the less stable the hierarchy is.

##### Example

This Shape hierarchy can be rewritten using interface inheritance:

    class Shape {  // pure interface
    public:
        virtual Point center() const = 0;
        virtual Color color() const = 0;

        virtual void rotate(int) = 0;
        virtual void move(Point p) = 0;

        virtual void redraw() = 0;

        // ...
    };

Note that a pure interface rarely has constructors: there is nothing to construct.

    class Circle : public Shape {
    public:
        Circle(Point c, int r, Color c) : cent{c}, rad{r}, col{c} { /* ... */ }

        Point center() const override { return cent; }
        Color color() const override { return col; }

        // ...
    private:
        Point cent;
        int rad;
        Color col;
    };

The interface is now less brittle, but there is more work in implementing the member functions.
For example, `center` has to be implemented by every class derived from `Shape`.

##### Example, dual hierarchy

How can we gain the benefit of stable hierarchies from interface hierarchies and the benefit of implementation reuse from implementation inheritance?
One popular technique is dual hierarchies.
There are many ways of implementing the idea of dual hierarchies; here, we use a multiple-inheritance variant.

First we devise a hierarchy of interface classes:

    class Shape {   // pure interface
    public:
        virtual Point center() const = 0;
        virtual Color color() const = 0;

        virtual void rotate(int) = 0;
        virtual void move(Point p) = 0;

        virtual void redraw() = 0;

        // ...
    };

    class Circle : public virtual Shape {   // pure interface
    public:
        virtual int radius() = 0;
        // ...
    };

To make this interface useful, we must provide its implementation classes (here, named equivalently, but in the `Impl` namespace):

    class Impl::Shape : public virtual ::Shape { // implementation
    public:
        // constructors, destructor
        // ...
        Point center() const override { /* ... */ }
        Color color() const override { /* ... */ }

        void rotate(int) override { /* ... */ }
        void move(Point p) override { /* ... */ }

        void redraw() override { /* ... */ }

        // ...
    };

Now `Shape` is a poor example of a class with an implementation,
but bear with us because this is just a simple example of a technique aimed at more complex hierarchies.

    class Impl::Circle : public virtual ::Circle, public Impl::Shape {   // implementation
    public:
        // constructors, destructor

        int radius() override { /* ... */ }
        // ...
    };

And we could extend the hierarchies by adding a Smiley class (:-)):

    class Smiley : public virtual Circle { // pure interface
    public:
        // ...
    };

    class Impl::Smiley : public virtual ::Smiley, public Impl::Circle {   // implementation
    public:
        // constructors, destructor
        // ...
    }

There are now two hierarchies:

* interface: Smiley -> Circle -> Shape
* implementation: Impl::Smiley -> Impl::Circle -> Impl::Shape

Since each implementation is derived from its interface as well as its implementation base class we get a lattice (DAG):

    Smiley     ->         Circle     ->  Shape
      ^                     ^               ^
      |                     |               |
    Impl::Smiley -> Impl::Circle -> Impl::Shape

As mentioned, this is just one way to construct a dual hierarchy.

The implementation hierarchy can be used directly, rather than through the abstract interface.

    void work_with_shape(Shape&);

    int user()
    {
        Impl::Smiley my_smiley{ /* args */ };   // create concrete shape
        // ...
        my_smiley.some_member();        // use implementation class directly
        // ...
        work_with_shape(my_smiley);     // use implementation through abstract interface
        // ...
    }

This can be useful when the implementation class has members that are not offered in the abstract interface
or if direct use of a member offers optimization opportunities (e.g., if an implementation member function is `final`)

##### Note

Another (related) technique for separating interface and implementation is [Pimpl](#Ri-pimpl).

##### Note

There is often a choice between offering common functionality as (implemented) base class functions and freestanding functions
(in an implementation namespace).
Base classes give a shorter notation and easier access to shared data (in the base)
at the cost of the functionality being available only to users of the hierarchy.

##### Enforcement

* Flag a derived to base conversion to a base with both data and virtual functions
(except for calls from a derived class member to a base class member)
* ???


### <a name="Rh-copy"></a>C.130: For making deep copies of polymorphic classes prefer a virtual `clone` function instead of public copy construction/assignment

##### Reason

Copying a polymorphic class is discouraged due to the slicing problem, see [C.67](#Rc-copy-virtual). If you really need copy semantics, copy deeply: Provide a virtual `clone` function that will copy the actual most-derived type and return an owning pointer to the new object, and then in derived classes return the derived type (use a covariant return type).

##### Example

    class B {
    public:
        B() = default;
        virtual ~B() = default;
        virtual gsl::owner<B*> clone() const = 0;
    protected:
         B(const B&) = default;
         B& operator=(const B&) = default;
         B(B&&) noexcept = default;
         B& operator=(B&&) noexcept = default;
        // ...
    };

    class D : public B {
    public:
        gsl::owner<D*> clone() const override
        {
            return new D{*this};
        };
    };

Generally, it is recommended to use smart pointers to represent ownership (see [R.20](#Rr-owner)). However, because of language rules, the covariant return type cannot be a smart pointer: `D::clone` can't return a `unique_ptr<D>` while `B::clone` returns `unique_ptr<B>`. Therefore, you either need to consistently return `unique_ptr<B>` in all overrides, or use `owner<>` utility from the [Guidelines Support Library](#SS-views).



### <a name="Rh-get"></a>C.131: Avoid trivial getters and setters

##### Reason

A trivial getter or setter adds no semantic value; the data item could just as well be `public`.

##### Example

    class Point {   // Bad: verbose
        int x;
        int y;
    public:
        Point(int xx, int yy) : x{xx}, y{yy} { }
        int get_x() const { return x; }
        void set_x(int xx) { x = xx; }
        int get_y() const { return y; }
        void set_y(int yy) { y = yy; }
        // no behavioral member functions
    };

Consider making such a class a `struct` -- that is, a behaviorless bunch of variables, all public data and no member functions.

    struct Point {
        int x {0};
        int y {0};
    };

Note that we can put default initializers on data members: [C.49: Prefer initialization to assignment in constructors](#Rc-initialize).

##### Note

The key to this rule is whether the semantics of the getter/setter are trivial. While it is not a complete definition of "trivial", consider whether there would be any difference beyond syntax if the getter/setter was a public data member instead. Examples of non-trivial semantics would be: maintaining a class invariant or converting between an internal type and an interface type.

##### Enforcement

Flag multiple `get` and `set` member functions that simply access a member without additional semantics.

### <a name="Rh-virtual"></a>C.132: Don't make a function `virtual` without reason

##### Reason

Redundant `virtual` increases run-time and object-code size.
A virtual function can be overridden and is thus open to mistakes in a derived class.
A virtual function ensures code replication in a templated hierarchy.

##### Example, bad

    template<class T>
    class Vector {
    public:
        // ...
        virtual int size() const { return sz; }   // bad: what good could a derived class do?
    private:
        T* elem;   // the elements
        int sz;    // number of elements
    };

This kind of "vector" isn't meant to be used as a base class at all.

##### Enforcement

* Flag a class with virtual functions but no derived classes.
* Flag a class where all member functions are virtual and have implementations.

### <a name="Rh-protected"></a>C.133: Avoid `protected` data

##### Reason

`protected` data is a source of complexity and errors.
`protected` data complicates the statement of invariants.
`protected` data inherently violates the guidance against putting data in base classes, which usually leads to having to deal with virtual inheritance as well.

##### Example, bad

    class Shape {
    public:
        // ... interface functions ...
    protected:
        // data for use in derived classes:
        Color fill_color;
        Color edge_color;
        Style st;
    };

Now it is up to every derived `Shape` to manipulate the protected data correctly.
This has been popular, but also a major source of maintenance problems.
In a large class hierarchy, the consistent use of protected data is hard to maintain because there can be a lot of code,
spread over a lot of classes.
The set of classes that can touch that data is open: anyone can derive a new class and start manipulating the protected data.
Often, it is not possible to examine the complete set of classes, so any change to the representation of the class becomes infeasible.
There is no enforced invariant for the protected data; it is much like a set of global variables.
The protected data has de facto become global to a large body of code.

##### Note

Protected data often looks tempting to enable arbitrary improvements through derivation.
Often, what you get is unprincipled changes and errors.
[Prefer `private` data](#Rc-private) with a well-specified and enforced invariant.
Alternative, and often better, [keep data out of any class used as an interface](#Rh-abstract).

##### Note

Protected member function can be just fine.

##### Enforcement

Flag classes with `protected` data.

### <a name="Rh-public"></a>C.134: Ensure all non-`const` data members have the same access level

##### Reason

Prevention of logical confusion leading to errors.
If the non-`const` data members don't have the same access level, the type is confused about what it's trying to do.
Is it a type that maintains an invariant or simply a collection of values?

##### Discussion

The core question is: What code is responsible for maintaining a meaningful/correct value for that variable?

There are exactly two kinds of data members:

* A: Ones that don't participate in the object's invariant. Any combination of values for these members is valid.
* B: Ones that do participate in the object's invariant. Not every combination of values is meaningful (else there'd be no invariant). Therefore all code that has write access to these variables must know about the invariant, know the semantics, and know (and actively implement and enforce) the rules for keeping the values correct.

Data members in category A should just be `public` (or, more rarely, `protected` if you only want derived classes to see them). They don't need encapsulation. All code in the system might as well see and manipulate them.

Data members in category B should be `private` or `const`. This is because encapsulation is important. To make them non-`private` and non-`const` would mean that the object can't control its own state: An unbounded amount of code beyond the class would need to know about the invariant and participate in maintaining it accurately -- if these data members were `public`, that would be all calling code that uses the object; if they were `protected`, it would be all the code in current and future derived classes. This leads to brittle and tightly coupled code that quickly becomes a nightmare to maintain. Any code that inadvertently sets the data members to an invalid or unexpected combination of values would corrupt the object and all subsequent uses of the object.

Most classes are either all A or all B:

* *All public*: If you're writing an aggregate bundle-of-variables without an invariant across those variables, then all the variables should be `public`.
  [By convention, declare such classes `struct` rather than `class`](#Rc-struct)
* *All private*: If you're writing a type that maintains an invariant, then all the non-`const` variables should be private -- it should be encapsulated.

##### Exception

Occasionally classes will mix A and B, usually for debug reasons. An encapsulated object might contain something like non-`const` debug instrumentation that isn't part of the invariant and so falls into category A -- it isn't really part of the object's value or meaningful observable state either. In that case, the A parts should be treated as A's (made `public`, or in rarer cases `protected` if they should be visible only to derived classes) and the B parts should still be treated like B's (`private` or `const`).

##### Enforcement

Flag any class that has non-`const` data members with different access levels.

### <a name="Rh-mi-interface"></a>C.135: Use multiple inheritance to represent multiple distinct interfaces

##### Reason

Not all classes will necessarily support all interfaces, and not all callers will necessarily want to deal with all operations.
Especially to break apart monolithic interfaces into "aspects" of behavior supported by a given derived class.

##### Example

    class iostream : public istream, public ostream {   // very simplified
        // ...
    };

`istream` provides the interface to input operations; `ostream` provides the interface to output operations.
`iostream` provides the union of the `istream` and `ostream` interfaces and the synchronization needed to allow both on a single stream.

##### Note

This is a very common use of inheritance because the need for multiple different interfaces to an implementation is common
and such interfaces are often not easily or naturally organized into a single-rooted hierarchy.

##### Note

Such interfaces are typically abstract classes.

##### Enforcement

???

### <a name="Rh-mi-implementation"></a>C.136: Use multiple inheritance to represent the union of implementation attributes

##### Reason

Some forms of mixins have state and often operations on that state.
If the operations are virtual the use of inheritance is necessary, if not using inheritance can avoid boilerplate and forwarding.

##### Example

    class iostream : public istream, public ostream {   // very simplified
        // ...
    };

`istream` provides the interface to input operations (and some data); `ostream` provides the interface to output operations (and some data).
`iostream` provides the union of the `istream` and `ostream` interfaces and the synchronization needed to allow both on a single stream.

##### Note

This a relatively rare use because implementation can often be organized into a single-rooted hierarchy.

##### Example

Sometimes, an "implementation attribute" is more like a "mixin" that determine the behavior of an implementation and inject
members to enable the implementation of the policies it requires.
For example, see `std::enable_shared_from_this`
or various bases from boost.intrusive (e.g. `list_base_hook` or `intrusive_ref_counter`).

##### Enforcement

???

### <a name="Rh-vbase"></a>C.137: Use `virtual` bases to avoid overly general base classes

##### Reason

 Allow separation of shared data and interface.
 To avoid all shared data to being put into an ultimate base class.

##### Example

    struct Interface {
        virtual void f();
        virtual int g();
        // ... no data here ...
    };

    class Utility {  // with data
        void utility1();
        virtual void utility2();    // customization point
    public:
        int x;
        int y;
    };

    class Derive1 : public Interface, virtual protected Utility {
        // override Interface functions
        // Maybe override Utility virtual functions
        // ...
    };

    class Derive2 : public Interface, virtual protected Utility {
        // override Interface functions
        // Maybe override Utility virtual functions
        // ...
    };

Factoring out `Utility` makes sense if many derived classes share significant "implementation details."


##### Note

Obviously, the example is too "theoretical", but it is hard to find a *small* realistic example.
`Interface` is the root of an [interface hierarchy](#Rh-abstract)
and `Utility` is the root of an [implementation hierarchy](#Rh-kind).
Here is [a slightly more realistic example](https://www.quora.com/What-are-the-uses-and-advantages-of-virtual-base-class-in-C%2B%2B/answer/Lance-Diduck) with an explanation.

##### Note

Often, linearization of a hierarchy is a better solution.

##### Enforcement

Flag mixed interface and implementation hierarchies.

### <a name="Rh-using"></a>C.138: Create an overload set for a derived class and its bases with `using`

##### Reason

Without a using declaration, member functions in the derived class hide the entire inherited overload sets.

##### Example, bad

    #include <iostream>
    class B {
    public:
        virtual int f(int i) { std::cout << "f(int): "; return i; }
        virtual double f(double d) { std::cout << "f(double): "; return d; }
        virtual ~B() = default;
    };
    class D: public B {
    public:
        int f(int i) override { std::cout << "f(int): "; return i + 1; }
    };
    int main()
    {
        D d;
        std::cout << d.f(2) << '\n';   // prints "f(int): 3"
        std::cout << d.f(2.3) << '\n'; // prints "f(int): 3"
    }

##### Example, good

    class D: public B {
    public:
        int f(int i) override { std::cout << "f(int): "; return i + 1; }
        using B::f; // exposes f(double)
    };

##### Note

This issue affects both virtual and non-virtual member functions

For variadic bases, C++17 introduced a variadic form of the using-declaration,

    template<class... Ts>
    struct Overloader : Ts... {
        using Ts::operator()...; // exposes operator() from every base
    };

##### Enforcement

Diagnose name hiding

### <a name="Rh-final"></a>C.139: Use `final` on classes sparingly

##### Reason

Capping a hierarchy with `final` classes is rarely needed for logical reasons and can be damaging to the extensibility of a hierarchy.

##### Example, bad

    class Widget { /* ... */ };

    // nobody will ever want to improve My_widget (or so you thought)
    class My_widget final : public Widget { /* ... */ };

    class My_improved_widget : public My_widget { /* ... */ };  // error: can't do that

##### Note

Not every class is meant to be a base class.
Most standard-library classes are examples of that (e.g., `std::vector` and `std::string` are not designed to be derived from).
This rule is about using `final` on classes with virtual functions meant to be interfaces for a class hierarchy.

##### Note

Claims of performance improvements from `final` should be substantiated.
Too often, such claims are based on conjecture or experience with other languages.

There are examples where `final` can be important for both logical and performance reasons.
One example is a performance-critical AST hierarchy in a compiler or language analysis tool.
New derived classes are not added every year and only by library implementers.
However, misuses are (or at least have been) far more common.

##### Enforcement

Flag uses of `final` on classes.


### <a name="Rh-virtual-default-arg"></a>C.140: Do not provide different default arguments for a virtual function and an overrider

##### Reason

That can cause confusion: An overrider does not inherit default arguments.

##### Example, bad

    class Base {
    public:
        virtual int multiply(int value, int factor = 2) = 0;
        virtual ~Base() = default;
    };

    class Derived : public Base {
    public:
        int multiply(int value, int factor = 10) override;
    };

    Derived d;
    Base& b = d;

    b.multiply(10);  // these two calls will call the same function but
    d.multiply(10);  // with different arguments and so different results

##### Enforcement

Flag default arguments on virtual functions if they differ between base and derived declarations.

## C.hier-access: Accessing objects in a hierarchy

### <a name="Rh-poly"></a>C.145: Access polymorphic objects through pointers and references

##### Reason

If you have a class with a virtual function, you don't (in general) know which class provided the function to be used.

##### Example

    struct B { int a; virtual int f(); virtual ~B() = default };
    struct D : B { int b; int f() override; };

    void use(B b)
    {
        D d;
        B b2 = d;   // slice
        B b3 = b;
    }

    void use2()
    {
        D d;
        use(d);   // slice
    }

Both `d`s are sliced.

##### Exception

You can safely access a named polymorphic object in the scope of its definition, just don't slice it.

    void use3()
    {
        D d;
        d.f();   // OK
    }

##### See also

[A polymorphic class should suppress copying](#Rc-copy-virtual)

##### Enforcement

Flag all slicing.

### <a name="Rh-dynamic_cast"></a>C.146: Use `dynamic_cast` where class hierarchy navigation is unavoidable

##### Reason

`dynamic_cast` is checked at run time.

##### Example

    struct B {   // an interface
        virtual void f();
        virtual void g();
        virtual ~B();
    };

    struct D : B {   // a wider interface
        void f() override;
        virtual void h();
    };

    void user(B* pb)
    {
        if (D* pd = dynamic_cast<D*>(pb)) {
            // ... use D's interface ...
        }
        else {
            // ... make do with B's interface ...
        }
    }

Use of the other casts can violate type safety and cause the program to access a variable that is actually of type `X` to be accessed as if it were of an unrelated type `Z`:

    void user2(B* pb)   // bad
    {
        D* pd = static_cast<D*>(pb);    // I know that pb really points to a D; trust me
        // ... use D's interface ...
    }

    void user3(B* pb)    // unsafe
    {
        if (some_condition) {
            D* pd = static_cast<D*>(pb);   // I know that pb really points to a D; trust me
            // ... use D's interface ...
        }
        else {
            // ... make do with B's interface ...
        }
    }

    void f()
    {
        B b;
        user(&b);   // OK
        user2(&b);  // bad error
        user3(&b);  // OK *if* the programmer got the some_condition check right
    }

##### Note

Like other casts, `dynamic_cast` is overused.
[Prefer virtual functions to casting](#Rh-use-virtual).
Prefer [static polymorphism](#???) to hierarchy navigation where it is possible (no run-time resolution necessary)
and reasonably convenient.

##### Note

Some people use `dynamic_cast` where a `typeid` would have been more appropriate;
`dynamic_cast` is a general "is kind of" operation for discovering the best interface to an object,
whereas `typeid` is a "give me the exact type of this object" operation to discover the actual type of an object.
The latter is an inherently simpler operation that ought to be faster.
The latter (`typeid`) is easily hand-crafted if necessary (e.g., if working on a system where RTTI is -- for some reason -- prohibited),
the former (`dynamic_cast`) is far harder to implement correctly in general.

Consider:

    struct B {
        const char* name {"B"};
        // if pb1->id() == pb2->id() *pb1 is the same type as *pb2
        virtual const char* id() const { return name; }
        // ...
    };

    struct D : B {
        const char* name {"D"};
        const char* id() const override { return name; }
        // ...
    };

    void use()
    {
        B* pb1 = new B;
        B* pb2 = new D;

        cout << pb1->id(); // "B"
        cout << pb2->id(); // "D"


        if (pb2->id() == "D") {         // looks innocent
            D* pd = static_cast<D*>(pb2);
            // ...
        }
        // ...
    }

The result of `pb2->id() == "D"` is actually implementation defined.
We added it to warn of the dangers of home-brew RTTI.
This code might work as expected for years, just to fail on a new machine, new compiler, or a new linker that does not unify character literals.

If you implement your own RTTI, be careful.

##### Exception

If your implementation provided a really slow `dynamic_cast`, you might have to use a workaround.
However, all workarounds that cannot be statically resolved involve explicit casting (typically `static_cast`) and are error-prone.
You will basically be crafting your own special-purpose `dynamic_cast`.
So, first make sure that your `dynamic_cast` really is as slow as you think it is (there are a fair number of unsupported rumors about)
and that your use of `dynamic_cast` is really performance critical.

We are of the opinion that current implementations of `dynamic_cast` are unnecessarily slow.
For example, under suitable conditions, it is possible to perform a `dynamic_cast` in [fast constant time](http://www.stroustrup.com/fast_dynamic_casting.pdf).
However, compatibility makes changes difficult even if all agree that an effort to optimize is worthwhile.

In very rare cases, if you have measured that the `dynamic_cast` overhead is material, you have other means to statically guarantee that a downcast will succeed (e.g., you are using CRTP carefully), and there is no virtual inheritance involved, consider tactically resorting `static_cast` with a prominent comment and disclaimer summarizing this paragraph and that human attention is needed under maintenance because the type system can't verify correctness. Even so, in our experience such "I know what I'm doing" situations are still a known bug source.

##### Exception

Consider:

    template<typename B>
    class Dx : B {
        // ...
    };

##### Enforcement

* Flag all uses of `static_cast` for downcasts, including C-style casts that perform a `static_cast`.
* This rule is part of the [type-safety profile](#Pro-type-downcast).

### <a name="Rh-ref-cast"></a>C.147: Use `dynamic_cast` to a reference type when failure to find the required class is considered an error

##### Reason

Casting to a reference expresses that you intend to end up with a valid object, so the cast must succeed. `dynamic_cast` will then throw if it does not succeed.

##### Example

    std::string f(Base& b)
    {
        return dynamic_cast<Derived&>(b).to_string();
    }

##### Enforcement

???

### <a name="Rh-ptr-cast"></a>C.148: Use `dynamic_cast` to a pointer type when failure to find the required class is considered a valid alternative

##### Reason

The `dynamic_cast` conversion allows to test whether a pointer is pointing at a polymorphic object that has a given class in its hierarchy. Since failure to find the class merely returns a null value, it can be tested during run time. This allows writing code that can choose alternative paths depending on the results.

Contrast with [C.147](#Rh-ref-cast), where failure is an error, and should not be used for conditional execution.

##### Example

The example below describes the `add` function of a `Shape_owner` that takes ownership of constructed `Shape` objects. The objects are also sorted into views, according to their geometric attributes.
In this example, `Shape` does not inherit from `Geometric_attributes`. Only its subclasses do.

    void add(Shape* const item)
    {
      // Ownership is always taken
      owned_shapes.emplace_back(item);

      // Check the Geometric_attributes and add the shape to none/one/some/all of the views

      if (auto even = dynamic_cast<Even_sided*>(item))
      {
        view_of_evens.emplace_back(even);
      }

      if (auto trisym = dynamic_cast<Trilaterally_symmetrical*>(item))
      {
        view_of_trisyms.emplace_back(trisym);
      }
    }

##### Notes

A failure to find the required class will cause `dynamic_cast` to return a null value, and de-referencing a null-valued pointer will lead to undefined behavior.
Therefore the result of the `dynamic_cast` should always be treated as if it might contain a null value, and tested.

##### Enforcement

* (Complex) Unless there is a null test on the result of a `dynamic_cast` of a pointer type, warn upon dereference of the pointer.

### <a name="Rh-smart"></a>C.149: Use `unique_ptr` or `shared_ptr` to avoid forgetting to `delete` objects created using `new`

##### Reason

Avoid resource leaks.

##### Example

    void use(int i)
    {
        auto p = new int {7};           // bad: initialize local pointers with new
        auto q = make_unique<int>(9);   // ok: guarantee the release of the memory-allocated for 9
        if (0 < i) return;              // maybe return and leak
        delete p;                       // too late
    }

##### Enforcement

* Flag initialization of a naked pointer with the result of a `new`
* Flag `delete` of local variable

### <a name="Rh-make_unique"></a>C.150: Use `make_unique()` to construct objects owned by `unique_ptr`s

See [R.23](#Rr-make_unique)

### <a name="Rh-make_shared"></a>C.151: Use `make_shared()` to construct objects owned by `shared_ptr`s

See [R.22](#Rr-make_shared)

### <a name="Rh-array"></a>C.152: Never assign a pointer to an array of derived class objects to a pointer to its base

##### Reason

Subscripting the resulting base pointer will lead to invalid object access and probably to memory corruption.

##### Example

    struct B { int x; };
    struct D : B { int y; };

    void use(B*);

    D a[] = { {1, 2}, {3, 4}, {5, 6} };
    B* p = a;     // bad: a decays to &a[0] which is converted to a B*
    p[1].x = 7;   // overwrite a[0].y

    use(a);       // bad: a decays to &a[0] which is converted to a B*

##### Enforcement

* Flag all combinations of array decay and base to derived conversions.
* Pass an array as a `span` rather than as a pointer, and don't let the array name suffer a derived-to-base conversion before getting into the `span`


### <a name="Rh-use-virtual"></a>C.153: Prefer virtual function to casting

##### Reason

A virtual function call is safe, whereas casting is error-prone.
A virtual function call reaches the most derived function, whereas a cast might reach an intermediate class and therefore
give a wrong result (especially as a hierarchy is modified during maintenance).

##### Example

    ???

##### Enforcement

See [C.146](#Rh-dynamic_cast) and ???

## <a name="SS-overload"></a>C.over: Overloading and overloaded operators

You can overload ordinary functions, function templates, and operators.
You cannot overload function objects.

Overload rule summary:

* [C.160: Define operators primarily to mimic conventional usage](#Ro-conventional)
* [C.161: Use non-member functions for symmetric operators](#Ro-symmetric)
* [C.162: Overload operations that are roughly equivalent](#Ro-equivalent)
* [C.163: Overload only for operations that are roughly equivalent](#Ro-equivalent-2)
* [C.164: Avoid implicit conversion operators](#Ro-conversion)
* [C.165: Use `using` for customization points](#Ro-custom)
* [C.166: Overload unary `&` only as part of a system of smart pointers and references](#Ro-address-of)
* [C.167: Use an operator for an operation with its conventional meaning](#Ro-overload)
* [C.168: Define overloaded operators in the namespace of their operands](#Ro-namespace)
* [C.170: If you feel like overloading a lambda, use a generic lambda](#Ro-lambda)

### <a name="Ro-conventional"></a>C.160: Define operators primarily to mimic conventional usage

##### Reason

Minimize surprises.

##### Example

    class X {
    public:
        // ...
        X& operator=(const X&); // member function defining assignment
        friend bool operator==(const X&, const X&); // == needs access to representation
                                                    // after a = b we have a == b
        // ...
    };

Here, the conventional semantics is maintained: [Copies compare equal](#SS-copy).

##### Example, bad

    X operator+(X a, X b) { return a.v - b.v; }   // bad: makes + subtract

##### Note

Non-member operators should be either friends or defined in [the same namespace as their operands](#Ro-namespace).
[Binary operators should treat their operands equivalently](#Ro-symmetric).

##### Enforcement

Possibly impossible.

### <a name="Ro-symmetric"></a>C.161: Use non-member functions for symmetric operators

##### Reason

If you use member functions, you need two.
Unless you use a non-member function for (say) `==`, `a == b` and `b == a` will be subtly different.

##### Example

    bool operator==(Point a, Point b) { return a.x == b.x && a.y == b.y; }

##### Enforcement

Flag member operator functions.

### <a name="Ro-equivalent"></a>C.162: Overload operations that are roughly equivalent

##### Reason

Having different names for logically equivalent operations on different argument types is confusing, leads to encoding type information in function names, and inhibits generic programming.

##### Example

Consider:

    void print(int a);
    void print(int a, int base);
    void print(const string&);

These three functions all print their arguments (appropriately). Conversely:

    void print_int(int a);
    void print_based(int a, int base);
    void print_string(const string&);

These three functions all print their arguments (appropriately). Adding to the name just introduced verbosity and inhibits generic code.

##### Enforcement

???

### <a name="Ro-equivalent-2"></a>C.163: Overload only for operations that are roughly equivalent

##### Reason

Having the same name for logically different functions is confusing and leads to errors when using generic programming.

##### Example

Consider:

    void open_gate(Gate& g);   // remove obstacle from garage exit lane
    void fopen(const char* name, const char* mode);   // open file

The two operations are fundamentally different (and unrelated) so it is good that their names differ. Conversely:

    void open(Gate& g);   // remove obstacle from garage exit lane
    void open(const char* name, const char* mode ="r");   // open file

The two operations are still fundamentally different (and unrelated) but the names have been reduced to their (common) minimum, opening opportunities for confusion.
Fortunately, the type system will catch many such mistakes.

##### Note

Be particularly careful about common and popular names, such as `open`, `move`, `+`, and `==`.

##### Enforcement

???

### <a name="Ro-conversion"></a>C.164: Avoid implicit conversion operators

##### Reason

Implicit conversions can be essential (e.g., `double` to `int`) but often cause surprises (e.g., `String` to C-style string).

##### Note

Prefer explicitly named conversions until a serious need is demonstrated.
By "serious need" we mean a reason that is fundamental in the application domain (such as an integer to complex number conversion)
and frequently needed. Do not introduce implicit conversions (through conversion operators or non-`explicit` constructors)
just to gain a minor convenience.

##### Example

    struct S1 {
        string s;
        // ...
        operator char*() { return s.data(); }  // BAD, likely to cause surprises
    };

    struct S2 {
        string s;
        // ...
        explicit operator char*() { return s.data(); }
    };

    void f(S1 s1, S2 s2)
    {
        char* x1 = s1;     // OK, but can cause surprises in many contexts
        char* x2 = s2;     // error (and that's usually a good thing)
        char* x3 = static_cast<char*>(s2); // we can be explicit (on your head be it)
    }

The surprising and potentially damaging implicit conversion can occur in arbitrarily hard-to spot contexts, e.g.,

    S1 ff();

    char* g()
    {
        return ff();
    }

The string returned by `ff()` is destroyed before the returned pointer into it can be used.

##### Enforcement

Flag all non-explicit conversion operators.

### <a name="Ro-custom"></a>C.165: Use `using` for customization points

##### Reason

To find function objects and functions defined in a separate namespace to "customize" a common function.

##### Example

Consider `swap`. It is a general (standard-library) function with a definition that will work for just about any type.
However, it is desirable to define specific `swap()`s for specific types.
For example, the general `swap()` will copy the elements of two `vector`s being swapped, whereas a good specific implementation will not copy elements at all.

    namespace N {
        My_type X { /* ... */ };
        void swap(X&, X&);   // optimized swap for N::X
        // ...
    }

    void f1(N::X& a, N::X& b)
    {
        std::swap(a, b);   // probably not what we wanted: calls std::swap()
    }

The `std::swap()` in `f1()` does exactly what we asked it to do: it calls the `swap()` in namespace `std`.
Unfortunately, that's probably not what we wanted.
How do we get `N::X` considered?

    void f2(N::X& a, N::X& b)
    {
        swap(a, b);   // calls N::swap
    }

But that might not be what we wanted for generic code.
There, we typically want the specific function if it exists and the general function if not.
This is done by including the general function in the lookup for the function:

    void f3(N::X& a, N::X& b)
    {
        using std::swap;  // make std::swap available
        swap(a, b);        // calls N::swap if it exists, otherwise std::swap
    }

##### Enforcement

Unlikely, except for known customization points, such as `swap`.
The problem is that the unqualified and qualified lookups both have uses.

### <a name="Ro-address-of"></a>C.166: Overload unary `&` only as part of a system of smart pointers and references

##### Reason

The `&` operator is fundamental in C++.
Many parts of the C++ semantics assume its default meaning.

##### Example

    class Ptr { // a somewhat smart pointer
        Ptr(X* pp) : p(pp) { /* check */ }
        X* operator->() { /* check */ return p; }
        X operator[](int i);
        X operator*();
    private:
        T* p;
    };

    class X {
        Ptr operator&() { return Ptr{this}; }
        // ...
    };

##### Note

If you "mess with" operator `&` be sure that its definition has matching meanings for `->`, `[]`, `*`, and `.` on the result type.
Note that operator `.` currently cannot be overloaded so a perfect system is impossible.
We hope to remedy that: [Operator Dot (R2)](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2015/n4477.pdf).
Note that `std::addressof()` always yields a built-in pointer.

##### Enforcement

Tricky. Warn if `&` is user-defined without also defining `->` for the result type.

### <a name="Ro-overload"></a>C.167: Use an operator for an operation with its conventional meaning

##### Reason

Readability. Convention. Reusability. Support for generic code

##### Example

    void cout_my_class(const My_class& c) // confusing, not conventional,not generic
    {
        std::cout << /* class members here */;
    }

    std::ostream& operator<<(std::ostream& os, const my_class& c) // OK
    {
        return os << /* class members here */;
    }

By itself, `cout_my_class` would be OK, but it is not usable/composable with code that rely on the `<<` convention for output:

    My_class var { /* ... */ };
    // ...
    cout << "var = " << var << '\n';

##### Note

There are strong and vigorous conventions for the meaning of most operators, such as

* comparisons (`==`, `!=`, `<`, `<=`, `>`, `>=`, and `<=>`),
* arithmetic operations (`+`, `-`, `*`, `/`, and `%`)
* access operations (`.`, `->`, unary `*`, and `[]`)
* assignment (`=`)

Don't define those unconventionally and don't invent your own names for them.

##### Enforcement

Tricky. Requires semantic insight.

### <a name="Ro-namespace"></a>C.168: Define overloaded operators in the namespace of their operands

##### Reason

Readability.
Ability for find operators using ADL.
Avoiding inconsistent definition in different namespaces

##### Example

    struct S { };
    S operator+(S, S);   // OK: in the same namespace as S, and even next to S
    S s;

    S r = s + s;

##### Example

    namespace N {
        struct S { };
        S operator+(S, S);   // OK: in the same namespace as S, and even next to S
    }

    N::S s;

    S r = s + s;  // finds N::operator+() by ADL

##### Example, bad

    struct S { };
    S s;

    namespace N {
        bool operator!(S a) { return true; }
        bool not_s = !s;
    }

    namespace M {
        bool operator!(S a) { return false; }
        bool not_s = !s;
    }

Here, the meaning of `!s` differs in `N` and `M`.
This can be most confusing.
Remove the definition of `namespace M` and the confusion is replaced by an opportunity to make the mistake.

##### Note

If a binary operator is defined for two types that are defined in different namespaces, you cannot follow this rule.
For example:

    Vec::Vector operator*(const Vec::Vector&, const Mat::Matrix&);

This might be something best avoided.

##### See also

This is a special case of the rule that [helper functions should be defined in the same namespace as their class](#Rc-helper).

##### Enforcement

* Flag operator definitions that are not in the namespace of their operands

### <a name="Ro-lambda"></a>C.170: If you feel like overloading a lambda, use a generic lambda

##### Reason

You cannot overload by defining two different lambdas with the same name.

##### Example

    void f(int);
    void f(double);
    auto f = [](char);   // error: cannot overload variable and function

    auto g = [](int) { /* ... */ };
    auto g = [](double) { /* ... */ };   // error: cannot overload variables

    auto h = [](auto) { /* ... */ };   // OK

##### Enforcement

The compiler catches the attempt to overload a lambda.

## <a name="SS-union"></a>C.union: Unions

A `union` is a `struct` where all members start at the same address so that it can hold only one member at a time.
A `union` does not keep track of which member is stored so the programmer has to get it right;
this is inherently error-prone, but there are ways to compensate.

A type that is a `union` plus an indicator of which member is currently held is called a *tagged union*, a *discriminated union*, or a *variant*.

Union rule summary:

* [C.180: Use `union`s to save Memory](#Ru-union)
* [C.181: Avoid "naked" `union`s](#Ru-naked)
* [C.182: Use anonymous `union`s to implement tagged unions](#Ru-anonymous)
* [C.183: Don't use a `union` for type punning](#Ru-pun)
* ???

### <a name="Ru-union"></a>C.180: Use `union`s to save memory

##### Reason

A `union` allows a single piece of memory to be used for different types of objects at different times.
Consequently, it can be used to save memory when we have several objects that are never used at the same time.

##### Example

    union Value {
        int x;
        double d;
    };

    Value v = { 123 };  // now v holds an int
    cout << v.x << '\n';    // write 123
    v.d = 987.654;  // now v holds a double
    cout << v.d << '\n';    // write 987.654

But heed the warning: [Avoid "naked" `union`s](#Ru-naked)

##### Example

    // Short-string optimization

    constexpr size_t buffer_size = 16; // Slightly larger than the size of a pointer

    class Immutable_string {
    public:
        Immutable_string(const char* str) :
            size(strlen(str))
        {
            if (size < buffer_size)
                strcpy_s(string_buffer, buffer_size, str);
            else {
                string_ptr = new char[size + 1];
                strcpy_s(string_ptr, size + 1, str);
            }
        }

        ~Immutable_string()
        {
            if (size >= buffer_size)
                delete[] string_ptr;
        }

        const char* get_str() const
        {
            return (size < buffer_size) ? string_buffer : string_ptr;
        }

    private:
        // If the string is short enough, we store the string itself
        // instead of a pointer to the string.
        union {
            char* string_ptr;
            char string_buffer[buffer_size];
        };

        const size_t size;
    };

##### Enforcement

???

### <a name="Ru-naked"></a>C.181: Avoid "naked" `union`s

##### Reason

A *naked union* is a union without an associated indicator which member (if any) it holds,
so that the programmer has to keep track.
Naked unions are a source of type errors.

##### Example, bad

    union Value {
        int x;
        double d;
    };

    Value v;
    v.d = 987.654;  // v holds a double

So far, so good, but we can easily misuse the `union`:

    cout << v.x << '\n';    // BAD, undefined behavior: v holds a double, but we read it as an int

Note that the type error happened without any explicit cast.
When we tested that program the last value printed was `1683627180` which is the integer value for the bit pattern for `987.654`.
What we have here is an "invisible" type error that happens to give a result that could easily look innocent.

And, talking about "invisible", this code produced no output:

    v.x = 123;
    cout << v.d << '\n';    // BAD: undefined behavior

##### Alternative

Wrap a `union` in a class together with a type field.

The C++17 `variant` type (found in `<variant>`) does that for you:

    variant<int, double> v;
    v = 123;        // v holds an int
    int x = get<int>(v);
    v = 123.456;    // v holds a double
    double w = get<double>(v);

##### Enforcement

???

### <a name="Ru-anonymous"></a>C.182: Use anonymous `union`s to implement tagged unions

##### Reason

A well-designed tagged union is type safe.
An *anonymous* union simplifies the definition of a class with a (tag, union) pair.

##### Example

This example is mostly borrowed from TC++PL4 pp216-218.
You can look there for an explanation.

The code is somewhat elaborate.
Handling a type with user-defined assignment and destructor is tricky.
Saving programmers from having to write such code is one reason for including `variant` in the standard.

    class Value { // two alternative representations represented as a union
    private:
        enum class Tag { number, text };
        Tag type; // discriminant

        union { // representation (note: anonymous union)
            int i;
            string s; // string has default constructor, copy operations, and destructor
        };
    public:
        struct Bad_entry { }; // used for exceptions

        ~Value();
        Value& operator=(const Value&);   // necessary because of the string variant
        Value(const Value&);
        // ...
        int number() const;
        string text() const;

        void set_number(int n);
        void set_text(const string&);
        // ...
    };

    int Value::number() const
    {
        if (type != Tag::number) throw Bad_entry{};
        return i;
    }

    string Value::text() const
    {
        if (type != Tag::text) throw Bad_entry{};
        return s;
    }

    void Value::set_number(int n)
    {
        if (type == Tag::text) {
            s.~string();      // explicitly destroy string
            type = Tag::number;
        }
        i = n;
    }

    void Value::set_text(const string& ss)
    {
        if (type == Tag::text)
            s = ss;
        else {
            new(&s) string{ss};   // placement new: explicitly construct string
            type = Tag::text;
        }
    }

    Value& Value::operator=(const Value& e)   // necessary because of the string variant
    {
        if (type == Tag::text && e.type == Tag::text) {
            s = e.s;    // usual string assignment
            return *this;
        }

        if (type == Tag::text) s.~string(); // explicit destroy

        switch (e.type) {
        case Tag::number:
            i = e.i;
            break;
        case Tag::text:
            new(&s) string(e.s);   // placement new: explicit construct
        }

        type = e.type;
        return *this;
    }

    Value::~Value()
    {
        if (type == Tag::text) s.~string(); // explicit destroy
    }

##### Enforcement

???

### <a name="Ru-pun"></a>C.183: Don't use a `union` for type punning

##### Reason

It is undefined behavior to read a `union` member with a different type from the one with which it was written.
Such punning is invisible, or at least harder to spot than using a named cast.
Type punning using a `union` is a source of errors.

##### Example, bad

    union Pun {
        int x;
        unsigned char c[sizeof(int)];
    };

The idea of `Pun` is to be able to look at the character representation of an `int`.

    void bad(Pun& u)
    {
        u.x = 'x';
        cout << u.c[0] << '\n';     // undefined behavior
    }

If you wanted to see the bytes of an `int`, use a (named) cast:

    void if_you_must_pun(int& x)
    {
        auto p = reinterpret_cast<std::byte*>(&x);
        cout << p[0] << '\n';     // OK; better
        // ...
    }

Accessing the result of a `reinterpret_cast` from the object's declared type to `char*`, `unsigned char*`, or `std::byte*` is defined behavior. (Using `reinterpret_cast` is discouraged,
but at least we can see that something tricky is going on.)

##### Note

Unfortunately, `union`s are commonly used for type punning.
We don't consider "sometimes, it works as expected" a conclusive argument.

C++17 introduced a distinct type `std::byte` to facilitate operations on raw object representation.  Use that type instead of `unsigned char` or `char` for these operations.

##### Enforcement

???
