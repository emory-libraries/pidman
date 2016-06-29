.. _DEVELOPER_NOTES:

Developer Notes
===============

As of pidman version 0.10, the pid noid sequence is managed based on
a sequence in the database using django-sequences.  Follow these instructions
if you need to adjust the pid sequence in a development or QA environment,
e.g. to jump past duplicate pids imported from production that are
causing collisions.  The process for determining and adjusting the
sequence is basically the same process that is used in the pid 0002
migration::

    from sequences.models import Sequence
    from pidman.pid.models import Pid
    from pidman.pid.noid import decode_noid, encode_noid

    # Current sequence value can be determined based on the largest pid
    # If you need to match a different system, decode the largest pid
    # from that pidmanager instance.
    max_noid = Pid.objects.all().order_by('pk').last().pid
    # decode to convert noid to corresponding integer
    last_val = decode_noid(max_noid)

    # retrieve the pid noid sequence and update the last value
    pid_seq = Sequence.objects.get(name=Pid.SEQUENCE_NAME)
    pid_seq.last = last_val
    pid_seq.save()


.. NOTE::

    The pid sequence should *NOT* be manually adjusted in production.

