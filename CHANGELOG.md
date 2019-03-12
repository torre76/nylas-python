nylas-python Changelog
======================

Unreleased (dev)
----------------
* You can now pass a list of `scopes` when calling `APIClient.authentication_url()`
  in order to enable
  [selective sync](https://docs.nylas.com/docs/how-to-use-selective-sync).
  Previously, we only set `scope=email` by default; now, the default is to use
  all scopes.

v4.4.0
------
* Add support for `revoke-all` endpoint.


v4.3.0
------
* Raise `UnsyncedError` when a message isn't ready to be retrieved yet (HTTP 202) when
fetching a raw message.


v4.2.0
------



v3.0.0
------

## Large changes

* The Nylas Python SDK now fully supports both Python 2.7 and Python 3.3+.
* The SDK has a new dependency: the
  [URLObject](https://pypi.python.org/pypi/URLObject) library.
  This dependency will be automatically installed when you upgrade.
* The SDK now automatically converts between timestamps and Python datetime
  objects. These automatic conversions are opt-in: your existing code should
  continue to work unmodified. See the "Timestamps and Datetimes"
  section of this document for more information.

## Small changes

* The SDK now has over 95% automated test coverage.
* Previously, trying to access the following model properties would raise an error:
  `Folder.threads`, `Folder.messages`, `Label.threads`, `Label.messages`.
  These properties should now work as expected.
* The `Thread` model now exposes the `last_message_received_timestamp` and
  `last_message_sent_timestamp` properties, obtained from the Nylas API.
* Previously, if you created a `Draft` object, saved it, and then
  deleted it without modifying it further, the deletion would fail silently.
  Now, the SDK will actually attempt to delete a newly-saved `Draft` object,
  and will raise an error if it is unable to do so.
* Previously, you could initialize an `APIClient` with an `api_server`
  value set to an `http://` URL. Now, `APIClient` will verify that the
  `api_server` value starts with `https://`, and will raise an error if it
  does not.
* The `APIClient` constructor no longers accepts the `auth_server` argument,
  as it was never used for anything.
* The `nylas.client.util.url_concat` and `nylas.client.util.generate_id`
  functions have been removed. These functions were meant for internal use,
  and were never documented or expected to be used by others.
* You can now pass a `state` argument to `APIClient.authentication_url`,
  as per the OAuth 2.0 spec.

## Timestamps and Datetimes

Some properties in the Nylas API use timestamp integers to represent a specific
moment in time, such as `Message.date`. The Python SDK now exposes new properties
that have converted these existing properties from integers to Python datetime
objects. You can still access the existing properties to get the timestamp
integer -- these new properties are just a convenient way to access Python
datetime objects, if you want them.

This table summarizes the new datetime properties, and which existing timestamp
properties they match up with.

| New Property (datetime)           | Existing Property (timestamp)            |
| --------------------------------- | ---------------------------------------- |
| `Message.received_at`             | `Message.date`                           |
| `Thread.first_message_at`         | `Thread.first_message_timestamp`         |
| `Thread.last_message_at`          | `Thread.last_message_timestamp`          |
| `Thread.last_message_received_at` | `Thread.last_message_received_timestamp` |
| `Thread.last_message_sent_at`     | `Thread.last_message_sent_timestamp`     |
| `Draft.last_modified_at`          | `Draft.date`                             |
| `Event.original_start_at`         | `Event.original_start_time`              |

You can also use datetime objects when filtering on models with the `.where()`
method. For example, if you wanted to find all messages that were received
before Jan 1, 2015, previously you would run this code:

```python
client.messages.where(received_before=1420070400).all()
```

That code will still work, but if you prefer, you can run this code instead:

```python
from datetime import datetime

client.messages.where(received_before=datetime(2015, 1, 1)).all()
```

You can now use datetimes with the following filters:

* `client.messages.where(received_before=datetime())`
* `client.messages.where(received_after=datetime())`
* `client.threads.where(last_message_before=datetime())`
* `client.threads.where(last_message_after=datetime())`
* `client.threads.where(started_before=datetime())`
* `client.threads.where(started_after=datetime())`


[Full Changelog](https://github.com/nylas/nylas-python/compare/v2.0.0...v3.0.0)


v2.0.0
------

Release May 18, 2017:
- Add support for expanded message view
- Remove deprecated "Inbox" name
- Send correct auth headers for account management
- Respect the offset parameter for restfulmodelcollection
- Add ability to revoke token

[Full Changelog](https://github.com/nylas/nylas-python/compare/v1.2.3...v2.0.0)


v1.2.3
------

Release August 9, 2016:
- Adds full-text search support for Messages and Threads

v1.2.2
------

Released March 25, 2016:
- API client now uses Bearer Token Authorization headers instead of Basic Auth

v1.2.1
------

Released February 5, 2016:
- Fixes a bug that prevented the offset parameter from being used in queries

v1.2.0
------

Released December 17, 2015:

- Deprecate tags and tag-related functions.
- Return message object when sending a draft
- Support passing parameters and request bodies on delete

v1.1.0
------

Released October 8, 2015:

- Add client.account property

v1.0.2
------

Released September 22, 2015:

- Add handling for 405 responses
- Surface SMTP server errors
- Expose Message attributes: events, snippet
- Expose Folder and Label attributes: object, account_id
- Expose Thread attribute: received_recent_date
- Expose Draft attributes: reply_to_message_id, reply_to, starred, snippet
- Expose File attributes: content_id, message_ids
- Expose "object" attribute on Calendar, Event, and Contact
- Add local token for tests

v1.0.1
------

Released September 17, 2015:

Expose "owner" attribute on Events
Clean up raw message data

v1.0.0
------

Released August 28, 2015:

Don't first save draft objects when a direct send is possible.
Remove deprecated namespaces support from SDK
Account management fixes and upgrade/downgrade changes
Added tests

v0.3.5
------
Drafts can now be sent without an implicit intermediate save to the mail provider.

