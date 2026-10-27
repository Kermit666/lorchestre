# book-router

book-router lets an agent answer a design question from the right section of
a programming book, and apply that book's reasoning to your code. Lorchestre's
Lead uses it as its first lens for real design decisions.

No books are included: they are copyrighted. book-router starts empty and
works without them; each book you add makes it more useful.

## Recommended books

These are the books it was built and tuned with. Buy the ones you want and add
them as described below.

| Book | Author | Use it for | Suggested id |
|---|---|---|---|
| Refactoring: Improving the Design of Existing Code | Martin Fowler | Code smells and behavior-preserving refactoring. The main source; start here. | `fowler-refactoring` |
| Clean Code | Robert C. Martin | Naming, function shape, comments, formatting, test hygiene. | `clean-code` |
| Domain-Driven Design: Tackling Complexity in the Heart of Software | Eric Evans | Domain modeling, aggregates, bounded contexts, strategic design. | `domain-driven-design` |
| Patterns of Enterprise Application Architecture | Martin Fowler | Layering, domain logic, data access, object-relational mapping. | `patterns-of-enterprise-application-architecture` |
| Designing Data-Intensive Applications | Martin Kleppmann | Storage, replication, partitioning, transactions, streams, consistency. | `designing-data-intensive-applications` |
| Release It! Design and Deploy Production-Ready Software | Michael T. Nygard | Stability patterns, failure modes, surviving real load and outages. | `release-it` |
| Growing Object-Oriented Software, Guided by Tests | Steve Freeman and Nat Pryce | Outside-in TDD, walking skeletons, object collaboration, mocks. | `growing-object-oriented-software-guided-by-tests` |
| Dependency Injection: Principles, Practices, and Patterns | Steven van Deursen and Mark Seemann | Composition roots, dependency wiring, lifetimes, avoiding service locators. | `dependency-injection-principles-practices-and-patterns` |

If you only buy one, take Refactoring: most of Lorchestre's refactoring work
leans on it. Add Release It! or Designing Data-Intensive Applications next if
you work on backends.

## Adding a book

There is no one-command importer yet. A book pack is a cleaned markdown copy
of the book, a structural index, and decision-oriented cards, registered in
`references/library/registry.json`; the format is described in
[references/book-pack-contract.md](references/book-pack-contract.md). Give
your agent the book file and that contract and ask it to build the pack, for
example: "build a book-router pack for ~/books/refactoring.epub as
fowler-refactoring, following book-pack-contract.md". Using the suggested id
keeps it matching the examples already in this skill.

Your books stay on your machine: rerunning `install.sh` keeps them.
