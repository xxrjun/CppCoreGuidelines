# Per: Performance {#S-performance}

??? should this section be in the main guide???

This section contains rules for people who need high performance or low-latency.
That is, these are rules that relate to how to use as little time and as few resources as possible to achieve a task in a predictably short time.
The rules in this section are more restrictive and intrusive than what is needed for many (most) applications.
Do not naïvely try to follow them in general code: achieving the goals of low latency requires extra work.

Performance rule summary:

* [Per.1: Don't optimize without reason](#Rper-reason)
* [Per.2: Don't optimize prematurely](#Rper-Knuth)
* [Per.3: Don't optimize something that's not performance critical](#Rper-critical)
* [Per.4: Don't assume that complicated code is necessarily faster than simple code](#Rper-simple)
* [Per.5: Don't assume that low-level code is necessarily faster than high-level code](#Rper-low)
* [Per.6: Don't make claims about performance without measurements](#Rper-measure)
* [Per.7: Design to enable optimization](#Rper-efficiency)
* [Per.10: Rely on the static type system](#Rper-type)
* [Per.11: Move computation from run time to compile time](#Rper-Comp)
* [Per.12: Eliminate redundant aliases](#Rper-alias)
* [Per.13: Eliminate redundant indirections](#Rper-indirect)
* [Per.14: Minimize the number of allocations and deallocations](#Rper-alloc)
* [Per.15: Do not allocate on a critical branch](#Rper-alloc0)
* [Per.16: Use compact data structures](#Rper-compact)
* [Per.17: Declare the most used member of a time-critical struct first](#Rper-struct)
* [Per.18: Space is time](#Rper-space)
* [Per.19: Access memory predictably](#Rper-access)
* [Per.30: Avoid context switches on the critical path](#Rper-context)

### <a name="Rper-reason"></a>Per.1: Don't optimize without reason

##### Reason

If there is no need for optimization, the main result of the effort will be more errors and higher maintenance costs.

##### Note

Some people optimize out of habit or because it's fun.

???

### <a name="Rper-Knuth"></a>Per.2: Don't optimize prematurely

##### Reason

Elaborately optimized code is usually larger and harder to change than unoptimized code.

???

### <a name="Rper-critical"></a>Per.3: Don't optimize something that's not performance critical

##### Reason

Optimizing a non-performance-critical part of a program has no effect on system performance.

##### Note

If your program spends most of its time waiting for the web or for a human, optimization of in-memory computation is probably useless.

Put another way: If your program spends 4% of its processing time doing
computation A and 40% of its time doing computation B, a 50% improvement on A is
only as impactful as a 5% improvement on B. (If you don't even know how much
time is spent on A or B, see <a href="#Rper-reason">Per.1</a> and <a
href="#Rper-Knuth">Per.2</a>.)

### <a name="Rper-simple"></a>Per.4: Don't assume that complicated code is necessarily faster than simple code

##### Reason

Simple code can be very fast. Optimizers sometimes do marvels with simple code

##### Example, good

    // clear expression of intent, fast execution

    vector<uint8_t> v(100000);

    for (auto& c : v)
        c = ~c;

##### Example, bad

    // intended to be faster, but is often slower

    vector<uint8_t> v(100000);

    for (size_t i = 0; i < v.size(); i += sizeof(uint64_t)) {
        uint64_t& quad_word = *reinterpret_cast<uint64_t*>(&v[i]);
        quad_word = ~quad_word;
    }

##### Note

???

???

### <a name="Rper-low"></a>Per.5: Don't assume that low-level code is necessarily faster than high-level code

##### Reason

Low-level code sometimes inhibits optimizations. Optimizers sometimes do marvels with high-level code.

##### Note

???

???

### <a name="Rper-measure"></a>Per.6: Don't make claims about performance without measurements

##### Reason

The field of performance is littered with myth and bogus folklore.
Modern hardware and optimizers defy naive assumptions; even experts are regularly surprised.

##### Note

Getting good performance measurements can be hard and require specialized tools.

##### Note

A few simple microbenchmarks using Unix `time` or the standard-library `<chrono>` can help dispel the most obvious myths.
If you can't measure your complete system accurately, at least try to measure a few of your key operations and algorithms.
A profiler can help tell you which parts of your system are performance critical.
Often, you will be surprised.

???

### <a name="Rper-efficiency"></a>Per.7: Design to enable optimization

##### Reason

Because we often need to optimize the initial design.
Because a design that ignores the possibility of later improvement is hard to change.

##### Example

From the C (and C++) standard:

    void qsort (void* base, size_t num, size_t size, int (*compar)(const void*, const void*));

When did you even want to sort memory?
Really, we sort sequences of elements, typically stored in containers.
A call to `qsort` throws away much useful information (e.g., the element type), forces the user to repeat information
already known (e.g., the element size), and forces the user to write extra code (e.g., a function to compare `double`s).
This implies added work for the programmer, is error-prone, and deprives the compiler of information needed for optimization.

    double data[100];
    // ... fill a ...

    // 100 chunks of memory of sizeof(double) starting at
    // address data using the order defined by compare_doubles
    qsort(data, 100, sizeof(double), compare_doubles);

From the point of view of interface design, `qsort` throws away useful information.

We can do better (in C++98)

    template<typename Iter>
        void sort(Iter b, Iter e);  // sort [b:e)

    sort(data, data + 100);

Here, we use the compiler's knowledge about the size of the array, the type of elements, and how to compare `double`s.

With C++20, we can do better still

    // sortable specifies that c must be a
    // random-access sequence of elements comparable with <
    void sort(sortable auto& c);

    sort(c);

The key is to pass sufficient information for a good implementation to be chosen.
In this, the `sort` interfaces shown here still have a weakness:
They implicitly rely on the element type having less-than (`<`) defined.
To complete the interface, we need a second version that accepts a comparison criterion:

    // compare elements of c using r
    template<random_access_range R, class C> requires sortable<R, C>
    void sort(R&& r, C c);

The standard-library specification of `sort` offers those two versions, and more.

##### Note

Premature optimization is said to be [the root of all evil](#Rper-Knuth), but that's not a reason to despise performance.
It is never premature to consider what makes a design amenable to improvement, and improved performance is a commonly desired improvement.
Aim to build a set of habits that by default results in efficient, maintainable, and optimizable code.
In particular, when you write a function that is not a one-off implementation detail, consider

* Information passing:
Prefer clean [interfaces](#S-interfaces) carrying sufficient information for later improvement of implementation.
Note that information flows into and out of an implementation through the interfaces we provide.
* Compact data: By default, [use compact data](#Rper-compact), such as `std::vector` and [access it in a systematic fashion](#Rper-access).
If you think you need a linked structure, try to craft the interface so that this structure isn't seen by users.
* Function argument passing and return:
Distinguish between mutable and non-mutable data.
Don't impose a resource management burden on your users.
Don't impose spurious run-time indirections on your users.
Use [conventional ways](#Rf-conventional) of passing information through an interface;
unconventional and/or "optimized" ways of passing data can seriously complicate later reimplementation.
* Abstraction:
Don't overgeneralize; a design that tries to cater for every possible use (and misuse) and defers every design decision for later
(using compile-time or run-time indirections) is usually a complicated, bloated, hard-to-understand mess.
Generalize from concrete examples, preserving performance as we generalize.
Do not generalize based on mere speculation about future needs.
The ideal is zero-overhead generalization.
* Libraries:
Use libraries with good interfaces.
If no library is available build one yourself and imitate the interface style from a good library.
The [standard library](#sl-the-standard-library) is a good first place to look for inspiration.
* Isolation:
Isolate your code from messy and/or old-style code by providing an interface of your choosing to it.
This is sometimes called "providing a wrapper" for the useful/necessary but messy code.
Don't let bad designs "bleed into" your code.

##### Example

Consider:

    template<class ForwardIterator, class T>
    bool binary_search(ForwardIterator first, ForwardIterator last, const T& val);

`binary_search(begin(c), end(c), 7)` will tell you whether `7` is in `c` or not.
However, it will not tell you where that `7` is or whether there are more than one `7`.

Sometimes, just passing the minimal amount of information back (here, `true` or `false`) is sufficient, but a good interface passes
needed information back to the caller. Therefore, the standard library also offers

    template<class ForwardIterator, class T>
    ForwardIterator lower_bound(ForwardIterator first, ForwardIterator last, const T& val);

`lower_bound` returns an iterator to the first match if any, otherwise to the first element greater than `val`, or `last` if no such element is found.

However, `lower_bound` still doesn't return enough information for all uses, so the standard library also offers

    template<class ForwardIterator, class T>
    pair<ForwardIterator, ForwardIterator>
    equal_range(ForwardIterator first, ForwardIterator last, const T& val);

`equal_range` returns a `pair` of iterators specifying the first and one beyond last match.

    auto r = equal_range(begin(c), end(c), 7);
    for (auto p = r.first; p != r.second; ++p)
        cout << *p << '\n';

Obviously, these three interfaces are implemented by the same basic code.
They are simply three ways of presenting the basic binary search algorithm to users,
ranging from the simplest ("make simple things simple!")
to returning complete, but not always needed, information ("don't hide useful information").
Naturally, crafting such a set of interfaces requires experience and domain knowledge.

##### Note

Do not simply craft the interface to match the first implementation and the first use case you think of.
Once your first initial implementation is complete, review it; once you deploy it, mistakes will be hard to remedy.

##### Note

A need for efficiency does not imply a need for [low-level code](#Rper-low).
High-level code isn't necessarily slow or bloated.

##### Note

Things have costs.
Don't be paranoid about costs (modern computers really are very fast),
but have a rough idea of the order of magnitude of cost of what you use.
For example, have a rough idea of the cost of
a memory access,
a function call,
a string comparison,
a system call,
a disk access,
and a message through a network.

##### Note

If you can only think of one implementation, you probably don't have something for which you can devise a stable interface.
Maybe, it is just an implementation detail - not every piece of code needs a stable interface - but pause and consider.
One question that can be useful is
"what interface would be needed if this operation should be implemented using multiple threads? be vectorized?"

##### Note

This rule does not contradict the [Don't optimize prematurely](#Rper-Knuth) rule.
It complements it, encouraging developers to enable later - appropriate and non-premature - optimization, if and where needed.

##### Enforcement

Tricky.
Maybe looking for `void*` function arguments will find examples of interfaces that hinder later optimization.

### <a name="Rper-type"></a>Per.10: Rely on the static type system

##### Reason

Type violations, weak types (e.g. `void*`s), and low-level code (e.g., manipulation of sequences as individual bytes) make the job of the optimizer much harder. Simple code often optimizes better than hand-crafted complex code.

???

### <a name="Rper-Comp"></a>Per.11: Move computation from run time to compile time

##### Reason

To decrease code size and run time.
To avoid data races by using constants.
To catch errors at compile time (and thus eliminate the need for error-handling code).

##### Example

    double square(double d) { return d*d; }
    static double s2 = square(2);    // old-style: dynamic initialization

    constexpr double ntimes(double d, int n)   // assume 0 <= n
    {
            double m = 1;
            while (n--) m *= d;
            return m;
    }
    constexpr double s3 {ntimes(2, 3)};  // modern-style: compile-time initialization

Code like the initialization of `s2` isn't uncommon, especially for initialization that's a bit more complicated than `square()`.
However, compared to the initialization of `s3` there are two problems:

* we suffer the overhead of a function call at run time
* `s2` just might be accessed by another thread before the initialization happens.

Note: you can't have a data race on a constant.

##### Example

Consider a popular technique for providing a handle for storing small objects in the handle itself and larger ones on the heap.

    constexpr int on_stack_max = 20;

    template<typename T>
    struct Scoped {     // store a T in Scoped
            // ...
        T obj;
    };

    template<typename T>
    struct On_heap {    // store a T on the free store
            // ...
            T* objp;
    };

    template<typename T>
    using Handle = typename std::conditional<(sizeof(T) <= on_stack_max),
                        Scoped<T>,      // first alternative
                        On_heap<T>      // second alternative
                   >::type;

    void f()
    {
        Handle<double> v1;                   // the double goes on the stack
        Handle<std::array<double, 200>> v2;  // the array goes on the free store
        // ...
    }

Assume that `Scoped` and `On_heap` provide compatible user interfaces.
Here we compute the optimal type to use at compile time.
There are similar techniques for selecting the optimal function to call.

##### Note

The ideal is *not* to try to execute everything at compile time.
Obviously, most computations depend on inputs, so they can't be moved to compile time,
but beyond that logical constraint is the fact that complex compile-time computation can seriously increase compile times
and complicate debugging.
It is even possible to slow down code by compile-time computation.
This is admittedly rare, but by factoring out a general computation into separate optimal sub-calculations, it is possible to render the instruction cache less effective.

##### Enforcement

* Look for simple functions that might be constexpr (but are not).
* Look for functions called with all constant-expression arguments.
* Look for macros that could be constexpr.

### <a name="Rper-alias"></a>Per.12: Eliminate redundant aliases

???

### <a name="Rper-indirect"></a>Per.13: Eliminate redundant indirections

???

### <a name="Rper-alloc"></a>Per.14: Minimize the number of allocations and deallocations

???

### <a name="Rper-alloc0"></a>Per.15: Do not allocate on a critical branch

???

### <a name="Rper-compact"></a>Per.16: Use compact data structures

##### Reason

Performance is typically dominated by memory access times.

???

### <a name="Rper-struct"></a>Per.17: Declare the most used member of a time-critical struct first

???

### <a name="Rper-space"></a>Per.18: Space is time

##### Reason

Performance is typically dominated by memory access times.

???

### <a name="Rper-access"></a>Per.19: Access memory predictably

##### Reason

Performance is very sensitive to cache performance, and cache algorithms favor simple (usually linear) access to adjacent data.

##### Example

    int matrix[rows][cols];

    // bad
    for (int c = 0; c < cols; ++c)
        for (int r = 0; r < rows; ++r)
            sum += matrix[r][c];

    // good
    for (int r = 0; r < rows; ++r)
        for (int c = 0; c < cols; ++c)
            sum += matrix[r][c];

### <a name="Rper-context"></a>Per.30: Avoid context switches on the critical path

???
