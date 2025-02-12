# GSL: Guidelines support library {#S-gsl}

The GSL is a small library of facilities designed to support this set of guidelines.
Without these facilities, the guidelines would have to be far more restrictive on language details.

The Core Guidelines support library is defined in namespace `gsl` and the names might be aliases for standard library or other well-known library names. Using the (compile-time) indirection through the `gsl` namespace allows for experimentation and for local variants of the support facilities.

The GSL is header only, and can be found at [GSL: Guidelines support library](https://github.com/Microsoft/GSL).
The support library facilities are designed to be extremely lightweight (zero-overhead) so that they impose no overhead compared to using conventional alternatives.
Where desirable, they can be "instrumented" with additional functionality (e.g., checks) for tasks such as debugging.

These Guidelines use types from the standard (e.g., C++17) in addition to ones from the GSL.
For example, we assume a `variant` type, but this is not currently in GSL.
Eventually, use [the one voted into C++17](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0088r3.html).

Some of the GSL types listed below might not be supported in the library you use due to technical reasons such as limitations in the current versions of C++.
Therefore, please consult your GSL documentation to find out more.

For each GSL type below we state an invariant for that type. That invariant holds as long as user code only changes the state of a GSL object using the type's provided member/free functions (i.e., user code does not bypass the type's interface to change the object's value/bits by violating any other Guidelines rule).

Summary of GSL components:

* [GSL.view: Views](#SS-views)
* [GSL.owner: Ownership pointers](#SS-ownership)
* [GSL.assert: Assertions](#SS-assertions)
* [GSL.util: Utilities](#SS-utilities)
* [GSL.concept: Concepts](#SS-gsl-concepts)

We plan for a "ISO C++ standard style" semi-formal specification of the GSL.

We rely on the ISO C++ Standard Library and hope for parts of the GSL to be absorbed into the standard library.

## <a name="SS-views"></a>GSL.view: Views

These types allow the user to distinguish between owning and non-owning pointers and between pointers to a single object and pointers to the first element of a sequence.

These "views" are never owners.

References are never owners (see [R.4](#Rr-ref)). Note: References have many opportunities to outlive the objects they refer to (returning a local variable by reference, holding a reference to an element of a vector and doing `push_back`, binding to `std::max(x, y + 1)`, etc). The Lifetime safety profile aims to address those things, but even so `owner<T&>` does not make sense and is discouraged.

The names are mostly ISO standard-library style (lower case and underscore):

* `T*`      // The `T*` is not an owner, might be null; assumed to be pointing to a single element.
* `T&`      // The `T&` is not an owner and can never be a "null reference"; references are always bound to objects.

The "raw-pointer" notation (e.g. `int*`) is assumed to have its most common meaning; that is, a pointer points to an object, but does not own it.
Owners should be converted to resource handles (e.g., `unique_ptr` or `vector<T>`) or marked `owner<T*>`.

* `owner<T*>`   // a `T*` that owns the object pointed/referred to; might be `nullptr`.

`owner` is used to mark owning pointers in code that cannot be upgraded to use proper resource handles.
Reasons for that include:

* Cost of conversion.
* The pointer is used with an ABI.
* The pointer is part of the implementation of a resource handle.

An `owner<T>` differs from a resource handle for a `T` by still requiring an explicit `delete`.

An `owner<T>` is assumed to refer to an object on the free store (heap).

If something is not supposed to be `nullptr`, say so:

* `not_null<T>`   // `T` is usually a pointer type (e.g., `not_null<int*>` and `not_null<owner<Foo*>>`) that must not be `nullptr`.
  `T` can be any type for which `==nullptr` is meaningful.

* `span<T>`       // `[p:p+n)`, constructor from `{p, q}` and `{p, n}`; `T` is the pointer type
* `span_p<T>`     // `{p, predicate}` `[p:q)` where `q` is the first element for which `predicate(*p)` is true

A `span<T>` refers to zero or more mutable `T`s unless `T` is a `const` type. All accesses to elements of the span, notably via `operator[]`, are guaranteed to be bounds-checked by default.

> Note: GSL's `span` (initially called `array_view`) was proposed for inclusion in the C++ standard library, and was adopted (with changes to its name and interface) except only that `std::span` does not provide for guaranteed bounds checking. Therefore GSL changed `span`'s name and interface to track `std::span` and should be exactly the same as `std::span`, and the only difference should be that GSL `span` is fully bounds-safe by default. If bounds-safety might affect its interface, then those change proposals should be brought back via the ISO C++ committee to keep `gsl::span` interface-compatible with `std::span`. If a future evolution of `std::span` adds bounds checking, `gsl::span` can be removed.

"Pointer arithmetic" is best done within `span`s.
A `char*` that points to more than one `char` but is not a C-style string (e.g., a pointer into an input buffer) should be represented by a `span`.

* `zstring`    // a `char*` supposed to be a C-style string; that is, a zero-terminated sequence of `char` or `nullptr`
* `czstring`   // a `const char*` supposed to be a C-style string; that is, a zero-terminated sequence of `const` `char` or `nullptr`

Logically, those last two aliases are not needed, but we are not always logical, and they make the distinction between a pointer to one `char` and a pointer to a C-style string explicit.
A sequence of characters that is not assumed to be zero-terminated should be a `span<char>`, or if that is impossible because of ABI issues a `char*`, rather than a `zstring`.


Use `not_null<zstring>` for C-style strings that cannot be `nullptr`. ??? Do we need a name for `not_null<zstring>`? or is its ugliness a feature?

## <a name="SS-ownership"></a>GSL.owner: Ownership pointers

* `unique_ptr<T>`     // unique ownership: `std::unique_ptr<T>`
* `shared_ptr<T>`     // shared ownership: `std::shared_ptr<T>` (a counted pointer)
* `stack_array<T>`    // A stack-allocated array. The number of elements is determined at construction and fixed thereafter. The elements are mutable unless `T` is a `const` type.
* `dyn_array<T>`      // A container, non-growing dynamically allocated array. The number of elements is determined at construction and fixed thereafter.
  The elements are mutable unless `T` is a `const` type. Basically a `span` that allocates and owns its elements.

## <a name="SS-assertions"></a>GSL.assert: Assertions

* `Expects`     // precondition assertion. Currently placed in function bodies. Later, should be moved to declarations.
                // `Expects(p)` terminates the program unless `p == true`
                // `Expects` is under control of some options (enforcement, error message, alternatives to terminate)
* `Ensures`     // postcondition assertion. Currently placed in function bodies. Later, should be moved to declarations.

These assertions are currently macros (yuck!) and must appear in function definitions (only)
pending standard committee decisions on contracts and assertion syntax.
See [the contract proposal](http://www.open-std.org/jtc1/sc22/wg21/docs/papers/2016/p0380r1.pdf); using the attribute syntax,
for example, `Expects(p)` will become `[[expects: p]]`.

## <a name="SS-utilities"></a>GSL.util: Utilities

* `finally`        // `finally(f)` makes a `final_action{f}` with a destructor that invokes `f`
* `narrow_cast`    // `narrow_cast<T>(x)` is `static_cast<T>(x)`
* `narrow`         // `narrow<T>(x)` is `static_cast<T>(x)` if `static_cast<T>(x) == x` with no signedness promotions, or it throws `narrowing_error` (e.g., `narrow<unsigned>(-42)` throws)
* `[[implicit]]`   // "Marker" to put on single-argument constructors to explicitly make them non-explicit.
* `move_owner`     // `p = move_owner(q)` means `p = q` but ???
* `joining_thread` // a RAII style version of `std::thread` that joins.
* `index`          // a type to use for all container and array indexing (currently an alias for `ptrdiff_t`)

## <a name="SS-gsl-concepts"></a>GSL.concept: Concepts

These concepts (type predicates) are borrowed from
Andrew Sutton's Origin library,
the Range proposal,
and the ISO WG21 Palo Alto TR.
Many of them are very similar to what became part of the ISO C++ standard in C++20.

* `String`
* `Number`
* `Boolean`
* `Range`              // in C++20, `std::ranges::range`
* `Sortable`           // in C++20, `std::sortable`
* `EqualityComparable` // in C++20, `std::equality_comparable`
* `Convertible`        // in C++20, `std::convertible_to`
* `Common`             // in C++20, `std::common_with`
* `Integral`           // in C++20, `std::integral`
* `SignedIntegral`     // in C++20, `std::signed_integral`
* `SemiRegular`        // in C++20, `std::semiregular`
* `Regular`            // in C++20, `std::regular`
* `TotallyOrdered`     // in C++20, `std::totally_ordered`
* `Function`           // in C++20, `std::invocable`
* `RegularFunction`    // in C++20, `std::regular_invocable`
* `Predicate`          // in C++20, `std::predicate`
* `Relation`           // in C++20, `std::relation`
* ...

### <a name="SS-gsl-smartptrconcepts"></a>GSL.ptr: Smart pointer concepts

* `Pointer`  // A type with `*`, `->`, `==`, and default construction (default construction is assumed to set the singular "null" value)
* `Unique_pointer`  // A type that matches `Pointer`, is movable, and is not copyable
* `Shared_pointer`   // A type that matches `Pointer`, and is copyable
