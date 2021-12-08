Modeling Authors, Quotes and Themes
-----------------------------------

The goal of our quotes app is for users to be able to submit their favorite quotes, discover new ones, and share categorized lists with their friends.

One-to-Many Relationships
^^^^^^^^^^^^^^^^^^^^^^^^^

Let's take things one step at a time, by starting with nearly the most basic structure possible. A quote has an author, and an author can have many quotes, so we start with a one-to-many relationship.

Quote
~~~~~

This is the "singular" side of the relationship, and so we need both a foreign key column and a relationship attribute for the related model instance.

.. code-block::

   # app/models/quote.py

   from flask_unchained.bundles.sqlalchemy import db

   class Quote(db.Model):
       class Meta:
           repr = ('id', 'quote', 'author')
           unique_together = ('quote', 'author_id')

       quote = db.Column(db.Text)

       author_id = db.foreign_key('Author')
       author = db.relationship('Author', back_populates='quotes')

       def __str__(self):
           return f'"{self.quote}" - {self.author.name}'

Author
~~~~~~

On the many side of the relationship, we only need a relationship attribute for the list of related models. Note the ``back_populates`` keyword argument on both sides: this specifies the name of the model attribute on the *other* side of the relationship.

.. code-block::

   # app/models/author.py

   from flask_unchained.bundles.sqlalchemy import db

   class Author(db.Model):
       class Meta:
           str = 'name'
           repr = ('id', 'name')

       name = db.Column(db.String, index=True, unique=True)

       quotes = db.relationship('Quote', back_populates='author', cascade='all, delete-orphan')

Many-to-Many Relationships
^^^^^^^^^^^^^^^^^^^^^^^^^^

It would be cool if the quotes in our database were categorized by themes - say, quotes about happiness or productivity or love. It is of course possible for a quote to have many themes, and for a theme to belong to many quotes. This is what is known as a many-to-many relationship.

QuoteTheme
~~~~~~~~~~

Whenever you have a many-to-many relationship, you need what's called a "join table." Often these tables will only store foreign keys to the models being joined (``Quote`` and ``Theme`` in this case), but it can also store extra columns containing information about the relationship (for example, we could have upvote and downvote counts for how users felt about how well a theme fit a quote). The join table is typically named by combining the names of the two models being joined, and looks like this:

.. code-block::

   # app/models/quote_theme.py

   from flask_unchained.bundles.sqlalchemy import db


   class QuoteTheme(db.Model):
       quote_id = db.foreign_key('Quote', primary_key=True)
       quote = db.relationship('Quote', back_populates='quote_themes')

       theme_id = db.foreign_key('Theme', primary_key=True)
       theme = db.relationship('Theme', back_populates='theme_quotes')

And we of course also need the opposite side of these relationships on our ``Quote`` and ``Theme`` models:

Quote
~~~~~

.. code-block::

   # app/models/quote.py

   from flask_unchained.bundles.sqlalchemy import db

   from .quote_theme import QuoteTheme


   class Quote(db.Model):
       # ...
       quote_themes = db.relationship('QuoteTheme', back_populates='quote',
                                      cascade='all, delete-orphan')
       themes = db.association_proxy('quote_themes', 'theme',
                                     creator=lambda theme: QuoteTheme(theme=theme))

Theme
~~~~~

.. code-block::

   # app/models/theme.py

   from flask_unchained.bundles.sqlalchemy import db

   from .quote_theme import QuoteTheme


   class Theme(db.Model):
       class Meta:
           str = 'name'
           repr = ('id', 'name')

       name = db.Column(db.String)
       description = db.Column(db.Text, nullable=True)

       theme_quotes = db.relationship('QuoteTheme', back_populates='theme',
                                      cascade='all, delete-orphan')
       quotes = db.association_proxy('theme_quotes', 'quote',
                                     creator=lambda quote: QuoteTheme(quote=quote))

Association Proxies
~~~~~~~~~~~~~~~~~~~

Unlike the one-to-many relationship between quotes and authors where there is a direct relationship between the models, here each side is directly related to the join table. By using an association proxy, we can make the interface on our models "hide" the implementation detail of the join table. What does that mean? By accessing ``Quote.themes``, we get back a list of ``Theme`` instances related only to that quote. By appending a new ``Theme`` to ``Quote.themes``, a new ``QuoteTheme`` will automatically be created in the database joining the theme to the quote.

.. admonition:: Implementation Notes
   :class: info

   If you've used Django's ORM before, these models should look quite similar. As for SQLAlchemy veterans, there's a bit of sugar going on here you won't find in "stock" SQLAlchemy. All models in Flask Unchained automatically get a ``__tablename__``, an ``id`` primary key column, as well as ``created_at`` and ``updated_at`` timestamp columns. These are all customizable using ``Meta`` attributes. The ``Meta.str`` option automatically implements ``__str__``, while ``Meta.repr`` is for ``__repr__``. You are of course able to implement these yourself without using any sugar and they will take precedence over the ``Meta`` options. There's also ``db.foreign_key`` and ``Meta.unique_together`` - these are all optional helpers meant to make your life a little easier. You can learn more in the :doc:`../bundles/sqlalchemy` documentation.

Database Migrations
^^^^^^^^^^^^^^^^^^^

Whenever you add or modify models, you must run database migrations so that the structure of the database and your code matches.

.. code:: shell

   flask db migrate -m 'add author, quote and theme models'
   flask db upgrade

Model Managers
^^^^^^^^^^^^^^

Flask Unchained encourages the use of services to handle shared implementation logic. One good use case for this is in managing models' interactions with the database. We call these model managers, and each of your application's models should get one.

Model Managers are the perfect place to store custom querying logic, as well as for handling interactions with the database session (eg saving, updating, and deleting instances - there are default implementations for these methods on the base ``ModelManager`` class). Another important advantage of using services is that they automatically support dependency injection.

AuthorManager
~~~~~~~~~~~~~

.. code-block::

   # app/managers/author_manager.py

   from typing import *

   from flask_unchained.bundles.sqlalchemy import db

   from ..models import Author


   class AuthorManager(db.ModelManager):
       class Meta:
           model = Author

       def all(self) -> List[Author]:
           return self.q.order_by('name').all()

QuoteManager
~~~~~~~~~~~~

.. code-block::

   # app/managers/quote_manager.py

   from typing import *

   from flask_unchained.bundles.sqlalchemy import db

   from ..models import Author, Quote


   class QuoteManager(db.ModelManager):
       class Meta:
           model = Quote

       def all(self) -> List[Quote]:
           return self.q.join(Author).order_by(Author.name).all()

ThemeManager
~~~~~~~~~~~~

.. code-block::

   # app/managers/theme_manager.py

   from typing import *

   from flask_unchained.bundles.sqlalchemy import db

   from ..models import Theme


   class ThemeManager(db.ModelManager):
       class Meta:
           model = Theme

       def all(self) -> List[Theme]:
           return self.q.order_by('name').all()

Database Fixtures
^^^^^^^^^^^^^^^^^

For now we'll load up some sample quotes using fixtures; next we'll implement some frontend forms so users can add their own quotes, and then add an admin interface for managing everything.

.. code-block:: yaml

   # app/fixtures.yaml

   Author:
     rumi:
       name: Rumi
     mark-twain:
       name: Mark Twain
     fm-alexander:
       name: F.M. Alexander
     eleanor-roosevelt:
       name: Eleanor Roosevelt
     henry-david-thoreau:
       name: Henry David Thoreau
     john-mason-good:
       name: John Mason Good
     shakespeare:
       name: Shakespeare
     abraham-maslow:
       name: Abraham Maslow

   Theme:
     passion:
       name: Passion
     getting-started:
       name: Getting Started
     productivity:
       name: Productivity
     habits:
       name: Habits
     dreams:
       name: Dreams
     growth:
       name: Growth
     happiness:
       name: Happiness
     fear:
       name: Fear

   Quote:
     quote1:
       quote: >-
         Let yourself be silently drawn by the strange pull of what you really love.
         It will not lead you astray.
       author: Author(rumi)
       themes:
         - Theme(passion)
     quote2:
       quote: >-
         The secret of getting ahead is getting started.
         The secret of getting started is breaking down your complex overwhelming tasks into small
         manageable tasks and then doing the first one.
       author: Author(mark-twain)
       themes: Theme(getting-started, productivity)
     quote3:
       quote: >-
         People do not decide their futures.
         They decide their habits, and their habits decide their futures.
       author: Author(fm-alexander)
       themes:
         - Theme(habits)
     quote4:
       quote: 'The future belongs to those who believe in the beauty of their dreams.'
       author: Author(eleanor-roosevelt)
       themes:
         - Theme(dreams)
     quote5:
       quote: >-
         If you have built castles in the air, your work need not be lost;
         that is where they should be. Now put foundations under them.
       author: Author(henry-david-thoreau)
       themes:
         - Theme(dreams)
     quote6:
       quote: >-
         Happiness consists in activity: such is the constitution of our nature;
         it is a running stream, not a stagnant pool.
       author: Author(john-mason-good)
       themes:
         - Theme(happiness)
     quote7:
       quote: "Things won are done; joy's soul lies in the doing."
       author: Author(shakespeare)
       themes: Theme(happiness, passion, productivity)
     quote8:
       quote: >-
         One can choose to go back toward safety or forward toward growth.
         Growth must be chosen again and again; fear must be overcome again and again.
       author: Author(abraham-maslow)
       themes: Theme(habits, growth, fear)

They can be imported like so:

.. code:: shell

   flask db import-fixtures app

Let's continue to :doc:`08_model_forms_and_views`.
