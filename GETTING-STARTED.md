# Getting Started with [musicaudit](https://github.com/jeffbeadles/musicaudit)

Notice: musicaudit treats your data as completely read-only. It will never write to, or change your data.

### How to install from Pypi
```console
    pip install musicaudit
```
and you can verify it's installed properly by running:
```console
    musicaudit --help
```

## You can save default options in ~/.config/musicaudit/config.yaml.  An example is
located at [Example configuration file](examples/config.sample.yaml)


## How to access your music collection; Two ways, Apple iTunes Library.xml and on disk

### You can point to the root of your music collection on disk.  Mine, for example is in ~/Music/<artist>/<album>/<song> and then use

`--path /path/to/top/of/music_collection`

### For iTunes, within iTunes, File -> Library -> Export Library, and save Library.xml and then use

`--apple-library /path/to/Library.xml`

#### Then, for each of the musicaudit commands, use the --path or --apple-library option you desire.  Note for Apple users, you can (and should) run musicaudit twice, once to check the iTunes data, and a second time to check your media files.  You will find that iTunes does not always update the music files with metadata like album artwork. (I speak from experience!)

### You can get a quick view of your library's health by running:
```console
    musicaudit health --path ~/Music
```

### You can run all known rules by running:
```console
    musicaudit rules --path ~/Music
```

### To see all available rules, run:
```console
    musicaudit rules --show-config --path ~/Music
```

### if there is a particular rule you want to investigate in detail, you can run it:
```console
    musicaudit rules --rule missing-artwork-track --path ~/Music --format json
```

### What is a good workflow for making changes to your music collection?

Here is my flow, now that I've been using musicaudit for some time, and it's saved me several times.

* Create a backup.
* Create a snapshot
```console
musicaudit snapshot --path ~/Music > ~/musicaudit-snapshot_before.json
```
* Make desired changes, to metadata, adding songs, etc...
* Create a second snapshot
```console
musicaudit snapshot --path ~/Music > ~/musicaudit-snapshot_after.json
```
* Review the differences between the snapshots to ensure no undesired changes
```console
musicaudit diff --old ~/musicaudit-snapshot_before.json --new ~/musicaudit-snapshot_after.json --format json
```
* If there are changes you do not want/expect, you can either revert from the backup, or use another tool to reverse the changes.  The diff command should identify exactly what has changed.  Only *you* know what should be done to repair it.


## Other information about musicaudit
###  Can I safely point musicaudit at my only copy of a 10,000+ track music collection?
#### Yes. musicaudit is non-destructive by design and by project contract.  It does not need write access to the music collection, and can work just fine with a read-only filesystem.
#### However, no software can protect against hardware failure, user error, or accidental deletion. Regardless of what tools you use, maintaining a current backup of your music collection is strongly recommended. (I speak from experience!)

### I am looking for a Mac tool to add lyrics to my music collection, do you have any suggestions?
#### I have used LyricsFinder, but there are several others.  You should find one that meeds your needs.	They are not associated with musicaudit.

