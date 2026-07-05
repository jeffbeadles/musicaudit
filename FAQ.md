# FAQ for [musicaudit](https://github.com/jeffbeadles/musicaudit)

## Getting Started

Notice: musicaudit treats your data as completely read-only, period.

### How to install:
    pip install musicaudit*.whl

and you can verify it's installed properly by running:

    musicaudit --help


### You can get a quick view of your library's health by running:

    musicaudit health --path ~/Music

### You can run all known rules by running:

    musicaudit rules --path ~/Music

### if there is a particular rule you want to investigate in detail, you can run it with:

    musicaudit rules --rule duplicate-track --path ~/Music --format json

### What is a good workflow for making changes to your music collection?

    Here is my flow, now that I've been using musicaudit for some time, and it's saved me several times.

    * Create a backup.
    * Create a snapshot
    ** musicaudit snapshot --path ~/Music > ~/musicaudit-snapshot_before.json
    * Make desired changes, to metadata, adding songs, etc...
    * Create a second snapshot
    ** musicaudit snapshot --path ~/Music > ~/musicaudit-snapshot_after.json
    * Review the differences between the snapshots to ensure no undesired changes
    ** musicaudit diff --old ~/musicaudit-snapshot_before.json --new ~/musicaudit-snapshot_after.json --format json
    * If there are changes you do not want/expect, you can either revert from the backup, or use another tool to reverse the changes.  The diff command should identify exactly what has changed.  Only *you* know what should be done to repair it.


## Other information about musicaudit
###  Can I safely point musicaudit at my only copy of a 10,000+ track music collection?
    Yes. musicaudit is non-destructive by design and by project contract.  It does not need write access to the music collection, and can work just fine with a read-only filesystem.

    However, no software can protect against hardware failure, user error, or accidental deletion. Regardless of what tools you use, maintaining a current backup of your music collection is strongly recommended. (I speak from experience!)

### I am looking for a Mac tool to add lyrics to my music collection, do you have any suggestions?
    I have used LyricsFinder, but there are several others.  You should find one that meeds your needs.	They are not associated with musicaudit.

