Features
========

Skill can have special features, functionality that are implemented by the container itself.
The following features are supported:

.. option:: kill (alternative: abort)

    The container implemented the kill feature. This means that the container can kill the skill by itself.
    If activated the broker can send a kill message ``taskKill``  to the container.
    The user can also send a abort message for the request ``requestAbort``.

.. option:: task

    The container implemented the task information feature. This means that the container can provide additional information about the task status.
    If activated the broker can send a task message ``task``  to the container.

