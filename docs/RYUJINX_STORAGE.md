# Ryujinx storage provider

This document describes the Ryujinx save-data storage model relevant to RyujinxSaveManager.

Its purpose is to separate:

1. facts established from Ryujinx, LibHac, and Nintendo Switch filesystem definitions;
2. behavior observed in real Ryujinx/Ryubing save trees;
3. implementation decisions made by RyujinxSaveManager;
4. areas that remain uncertain or version-dependent.

Game-specific save formats do **not** belong here. For example, the meaning of `rp_savedata.dat` belongs in the NSMBU Deluxe documentation.

## Evidence labels

Where the distinction matters, this document uses the following confidence terminology:

* **CONFIRMED** — directly supported by implementation source, an authoritative structure definition, or repeatable project fixtures.
* **HIGH CONFIDENCE** — supported by multiple strong sources but not yet verified across every target Ryujinx/Ryubing version.
* **TENTATIVE** — plausible and supported by some evidence, but not safe to rely on for writes.
* **UNKNOWN** — not sufficiently understood.

A fact being confirmed for a historical Ryujinx version does **not** imply that every fork and later version implements it identically.

---

# 1. Scope

`RyujinxStorageProvider` operates on Ryujinx save-data storage.

The initial implementation accepts a caller-provided `Path` representing a Ryujinx **user save root**, normally equivalent to:

```text
<Ryujinx data root>/bis/user/save
```

Historical Ryujinx source constructs user-save paths as:

```text
user/save/<SaveDataId as 16 hexadecimal digits>
```

and uses the emulator NAND path as their base.[1]

The provider does not assume that the filesystem hosting that path corresponds to the operating system running Python.

For example, development under WSL may inspect a Windows Ryujinx installation through a path such as:

```text
/mnt/c/Users/<user>/AppData/Roaming/Ryujinx/bis/user/save
```

The storage provider must therefore reason about the directory tree it receives, not infer storage semantics from `sys.platform`.

Automatic Ryujinx installation discovery is a separate concern and is not required by the basic scanner.

---

# 2. Save-data spaces

A Nintendo Switch save is not conceptually just a file associated with a Title ID.

The Switch filesystem exposes several save-data spaces. Current libnx definitions include:

```text
System
User
SdSystem
Temporary
SdUser
ProperSystem
SafeMode
```

as distinct `FsSaveDataSpaceId` values.[2]

For RyujinxSaveManager, an immediately relevant distinction is between user and system save storage. Historical Ryujinx source explicitly enumerates system saves from:

```text
system:/save
```

and treats them separately from user saves.[3]

Therefore:

> Scanning only `bis/user/save` does not imply discovery of every save-data object managed by Ryujinx.

The initial provider may intentionally support only user saves. That is a scope limitation, not an assumption about the complete Ryujinx filesystem.

Future storage support may need to understand additional save-data spaces and types.

---

# 3. Save-data types

Save-data **space** and save-data **type** are separate concepts.

Current libnx definitions expose the following `FsSaveDataType` values:[2]

```text
0 = System
1 = Account
2 = BCAT
3 = Device
4 = Temporary
5 = Cache
6 = SystemBCAT
```

The Switch filesystem also exposes different open operations for account, BCAT, device, temporary, cache, system, and system-BCAT save data.[2]

This means RyujinxSaveManager must not model every save as:

```text
Game + User = Save
```

That is common for account save data, but it is not the complete Switch save-data model.

---

# 4. SaveDataId versus Application ID / Title ID

Directories directly below a Ryujinx user-save root commonly have names such as:

```text
0000000000000001
0000000000000002
0000000000000003
```

Historical Ryujinx source constructs these paths using:

```text
user/save/{saveDataId:x16}
```

which establishes that the physical directory name is derived from a **SaveDataId**.[1]

This is not necessarily the game's Application ID / Title ID.

The distinction is fundamental:

```text
SaveDataId
    = identifier of the physical/logical save-data object

ApplicationId / Title ID
    = identifier of an application associated with save data
```

libnx likewise models `save_data_id` and `application_id` as distinct fields in `FsSaveDataInfo`.[2]

A scanner must therefore never infer:

```text
container directory name == Title ID
```

even though both identifiers are commonly displayed as 16 hexadecimal digits.

**Confidence: CONFIRMED.**

---

# 5. Directory-backed save-data representation

Ryujinx/LibHac has historically represented save data using directory-backed save filesystems.

A commonly observed user-save container looks like:

```text
bis/
└── user/
    └── save/
        └── <SaveDataId>/
            ├── 0/
            │   └── <game-defined filesystem>
            ├── 1/
            │   └── <game-defined filesystem>
            ├── ExtraData0
            └── ExtraData1
```

A contemporary Ryubing issue provides a real-world example with `0`, `1`, `ExtraData0`, and `ExtraData1` as siblings.[4]

Historical Ryujinx/LibHac changes also explicitly describe extending "directory save data" to store `SaveDataExtraData`.[5]

Other implementation-related entries may exist and must not be assumed absent.

---

# 6. `0` and `1`: committed and working directories

Historical Ryujinx source explicitly constructs:

```text
committedPath = <save root>/0
workingPath   = <save root>/1
```

and states that the committed directory is loaded on the next save-data mount when it exists. If the committed directory does not exist, the working directory is used; if the working directory is also absent, Ryujinx creates it.[1]

Therefore, for the historical implementation examined:

```text
0 = committed directory
1 = working directory
```

**Confidence: CONFIRMED for the referenced Ryujinx implementation.**

This should not be generalized into an undocumented promise that every future Ryujinx-derived emulator must use exactly the same transaction implementation.

Most importantly, these directories are **not game save slots**.

RyujinxSaveManager must never expose them as:

```text
Save Slot 0
Save Slot 1
```

A game's own save-slot concept exists inside the game-defined payload filesystem and is unrelated to these transaction-directory names.

---

# 7. Mount selection and recovery behavior

Historical Ryujinx's user-facing "open save directory" implementation contains an especially useful description of the mount behavior:

```text
if 0 exists:
    0 will be loaded on the next mount
else:
    1 will be loaded on the next mount
```

with `1` created if neither directory exists.[1]

This gives us strong evidence for interpreting the two directory names.

It does **not**, by itself, completely document the internal LibHac transaction algorithm.

Questions that still require source-level or fixture-backed verification include:

* exact directory rename/copy sequence during commit;
* when both directories normally coexist;
* how an interrupted commit is recovered;
* exact relationship between `ExtraData0`/`ExtraData1` and the directory transaction;
* how this behavior changed between LibHac versions.

Those details must remain outside write logic until verified.

---

# 8. Game-defined contents

The filesystem inside the active save payload is game-defined.

A game may contain one file:

```text
0/
└── rp_savedata.dat
```

while another may contain multiple files or nested directories.

A real Ryubing issue concerning Inazuma Eleven: Victory Road reports a game payload containing:

```text
SYSTEM/
HEADERSAVE/
AUTOSAVE/
```

and observes the same game-level structure within both transaction directories.[4]

Therefore the storage provider must treat payload contents as an **arbitrary filesystem tree**.

It must support:

* zero or more files;
* zero or more directories;
* nested directories;
* game-defined filenames;
* game-defined binary formats.

The generic storage provider must never assume:

* one save file per game;
* a specific filename;
* a specific extension;
* flat directory contents;
* one game-level save slot.

Those assumptions belong exclusively to game plugins and only when supported by evidence.

**Confidence: CONFIRMED.**

---

# 9. `ExtraData0` and `ExtraData1`

`ExtraData0` and `ExtraData1` are not game-defined payload files.

Historical LibHac/Ryujinx changes explicitly added `SaveDataExtraData` storage to directory save data.[5]

The Switch filesystem API exposes `FsSaveDataExtraData`, whose structure is documented by libnx.[2]

Independent Ryujinx tooling also reads `ExtraData0` to obtain the Application ID when scanning Ryujinx save containers.[6]

The exact transactional relationship between the numbered metadata copies and the numbered payload directories should still be verified before RyujinxSaveManager modifies either metadata file.

---

# 10. `SaveDataExtraData`

Current libnx defines `FsSaveDataExtraData` as containing:[2]

```text
FsSaveDataAttribute attr
u64                 owner_id
u64                 timestamp
u32                 flags
u32                 unknown/reserved
s64                 data_size
s64                 journal_size
u64                 commit_id
u8                  unused[0x190]
```

The structure therefore occupies:

```text
0x200 bytes
```

or:

```text
512 bytes
```

The metadata contains substantially more information than an Application ID.

**Confidence: CONFIRMED for the documented Switch/libnx structure.**

RyujinxSaveManager should still verify serialized Ryujinx fixtures before treating every arbitrary 512-byte `ExtraData*` file as valid.

---

# 11. `SaveDataAttribute`

The first member of `SaveDataExtraData` is `FsSaveDataAttribute`.

Current libnx defines it as containing:[2]

```text
offset  size   field
------  ----   --------------------------------
0x00    0x08   application_id
0x08    0x10   account UID
0x18    0x08   system_save_data_id
0x20    0x01   save_data_type
0x21    0x01   save_data_rank
0x22    0x02   save_data_index
0x24    0x04   padding
0x28    0x08   unknown/reserved
0x30    0x08   unknown/reserved
0x38    0x08   unknown/reserved
```

The structure is therefore `0x40` bytes long.

libnx documents the unknown fields at `0x28`, `0x30`, and `0x38` as zero for System and Account save-data types.[2]

RyujinxSaveManager should retain their names as unknown/reserved unless stronger evidence establishes their meaning.

---

# 12. Remaining `SaveDataExtraData` layout

Combining the documented member ordering and sizes gives the following layout:[2]

```text
offset  size    field
------  ------  --------------------------------
0x00    0x40    SaveDataAttribute
0x40    0x08    owner_id
0x48    0x08    timestamp
0x50    0x04    flags
0x54    0x04    unknown / normally zero
0x58    0x08    data_size
0x60    0x08    journal_size
0x68    0x08    commit_id
0x70    0x190   unused / uninitialized
```

Total:

```text
0x200
```

libnx describes:

* `owner_id` as the Program ID of the save-data owner, or zero for System save data;
* `timestamp` as a POSIX timestamp;
* `data_size` as usable save-data size;
* `journal_size` as save journal size;
* `commit_id` as the ID of the latest commit.[2]

The data and journal sizes are logical save-data allocation information and must not automatically be interpreted as the host filesystem space occupied by Ryujinx's directory representation.

---

# 13. Application ID / Title ID extraction

The first eight bytes of `SaveDataAttribute` are the `application_id` field.[2]

Independent tooling confirms the practical usefulness of this: SESS scans Ryujinx save directories and extracts a Title ID from `ExtraData0`.[6]

Read-only inspection of three private Ryujinx containers confirms little-endian
Application ID serialization in Account, Device, and BCAT saves. Two containers
share `01006F8002326000` (Device and BCAT); another has
`0100EA80032EA000` (Account). These are distinct from their physical
SaveDataIds. **Confidence: HIGH CONFIDENCE for these observed records**; the
complete metadata semantics of every emulator version remain unverified.

However, this must not be implemented as an unvalidated:

```python
title_id = int.from_bytes(file.read(8), "little")
```

against arbitrary files.

A robust parser should establish at least:

* expected metadata size;
* save-data type, while retaining unknown numeric values;
* structurally plausible fields where their meaning is known;
* correct serialization/endianness from fixtures;
* behavior when metadata copies disagree;
* behavior for historical or incomplete metadata.

Current discovery requires both `ExtraData` copies to be `0x200` bytes and to
agree on Application ID, AccountUid, SystemSaveDataId, and save-data type before
exposing the ID or type. It does not require zero padding or interpret unknown
fields. A single copy remains unidentified by project policy, and conflicting
copies receive a diagnostic; neither copy is selected as authoritative.

---

# 14. Account UID

`FsSaveDataAttribute` contains an `AccountUid` immediately after `application_id`.[2]

This means account save metadata can identify the Switch account associated with the save-data object.

This value is distinct from:

* SaveDataId;
* ApplicationId;
* SystemSaveDataId;
* OwnerId.

RyujinxSaveManager should model these concepts separately.

A future normalized metadata model may contain:

```text
save_data_id
application_id
user_id
system_save_data_id
save_data_type
save_data_rank
save_data_index
owner_id
commit_id
```

rather than conflating them into a generic identifier.

---

# 15. Save-data type affects interpretation

Metadata interpretation depends on `save_data_type`.

libnx specifically documents `system_save_data_id` as zero for Account save data, while the filesystem API exposes separate operations for account, device, BCAT, temporary, cache, system, and system-BCAT saves.[2]

Therefore:

> RyujinxSaveManager must not label every value at offset `0x00` as a user-game Title ID without considering the surrounding save-data metadata.

The same binary structure can participate in different save-data contexts.

---

# 16. Owner ID

`owner_id` is separate from `application_id`.

libnx describes it as the Program ID of the owner of the save data and specifies zero for System save data.[2]

Do not collapse:

```text
ApplicationId
OwnerId
SystemSaveDataId
```

into one "title" field.

They have distinct meanings.

---

# 17. Commit ID

`SaveDataExtraData` contains:

```text
commit_id
```

which libnx describes as the ID of the latest commit.[2]

This may eventually be useful for transaction-state inspection and recovery analysis.

However, RyujinxSaveManager must **not** invent an algorithm such as:

```text
larger CommitId == authoritative bank
```

without verifying LibHac's actual directory-save transaction logic.

The existence and broad meaning of `commit_id` are confirmed.

Its exact role in selecting between `0`, `1`, `ExtraData0`, and `ExtraData1` remains insufficiently verified for write decisions.

---

# 18. ExtraData copies and transaction state

Observed Ryujinx-derived save containers can contain:

```text
0/
1/
ExtraData0
ExtraData1
```

together.[4]

Historical LibHac/Ryujinx changes establish that directory save data stores `SaveDataExtraData` and uses locking/transactional filesystem machinery.[5]

It is therefore reasonable to treat `ExtraData0` and `ExtraData1` as implementation state associated with the directory save-data representation.

However, until the exact LibHac algorithm is documented from source and fixtures, RyujinxSaveManager must not:

* copy one ExtraData file over the other;
* choose one solely from modification time;
* update `commit_id` independently;
* regenerate ExtraData from partial knowledge;
* delete one because the other appears valid.

Game plugins should normally have no reason to modify these files.

**Exact copy-to-bank correspondence: TENTATIVE until verified.**

---

# 19. Historical metadata migration

Ryujinx's 2021 update to LibHac 0.13.1 explicitly added `SaveDataExtraData` storage to directory save data.[5]

The same Ryujinx update states that previously created saves lacked the extra data now needed for filesystem access-control checks. Ryujinx added logic to recreate missing save-data extra data on emulator startup.[5]

Historical Ryujinx source also contains repair logic that reads extra data and reconstructs missing fields using save-data index information.[3]

Therefore historical save trees may contain or have originated from:

* missing extra data;
* metadata created by older LibHac versions;
* partially reconstructed metadata;
* containers repaired from save-data index information.

Metadata absence must therefore produce a diagnostic rather than automatically causing the payload to be rejected as "not a save."

**Confidence: CONFIRMED historically.**

---

# 20. Directory locking

The LibHac 0.13.1 update integrated by Ryujinx explicitly states that directory save data was extended to lock the save directory so only one accessor could use it at a time.[5]

This is operationally important.

RyujinxSaveManager should assume that modifying save data while Ryujinx is actively accessing it may be unsafe.

Future write support should therefore prefer:

```text
Ryujinx stopped / save not actively mounted
```

before mutation.

The application must not bypass, remove, or ignore an unfamiliar lock merely to obtain write access.

The exact on-disk lock representation and its behavior in every supported Ryujinx/Ryubing version still require fixture-backed verification.

---

# 21. `saveMeta`

Historical Ryujinx code shows a second path associated with user save data:

```text
user/saveMeta/<SaveDataId>
```

In one deletion path, Ryujinx explicitly removes both:

```text
user/save/<SaveDataId>
user/saveMeta/<SaveDataId>
```

for the same `SaveDataId`.[7]

Therefore `saveMeta` is part of the broader Ryujinx save-data subsystem even though it is outside the physical payload container currently scanned by `RyujinxStorageProvider`.

RyujinxSaveManager must not assume that everything relevant to Ryujinx's save bookkeeping lives under:

```text
bis/user/save
```

The exact current purpose, format, and restoration requirements of `saveMeta` should be investigated before the application claims it can reconstruct a completely absent Ryujinx save-data record.

---

# 22. Save-data indexer

Historical Ryujinx repair code explicitly discusses save-data directories that exist but are not present in the save-data indexer.[3]

For certain system saves, the source notes that recreating the save adds it to the indexer while leaving existing directory contents intact.[3]

This establishes an important architectural distinction:

```text
physical save directory
```

is not necessarily identical to:

```text
fully indexed save-data object known to the emulator
```

RyujinxSaveManager's filesystem scanner therefore discovers **candidate physical save containers**.

It does not reproduce Ryujinx/LibHac's complete save-data service.

**Confidence: CONFIRMED historically.**

---

# 23. System saves

Historical Ryujinx source enumerates save-data directories from:

```text
system:/save
```

and contains special repair logic for system save data.[3]

The Switch filesystem API likewise distinguishes System save-data space and System save-data type from Account/User saves.[2]

Therefore the architecture should allow future providers/scopes for system save data.

The initial `RyujinxStorageProvider` may deliberately remain limited to:

```text
bis/user/save
```

as long as this limitation is explicit.

---

# 24. One game may not equal one save container

The Switch save-data model includes:

* save-data space;
* save-data type;
* application ID;
* account UID;
* system save-data ID;
* save-data index;
* save-data rank;
* physical SaveDataId.[2]

Therefore RyujinxSaveManager should not architecturally require:

```text
one ApplicationId == exactly one SaveDataContainer
```

A safer model permits:

```text
Game
└── one or more SaveDataContainer objects
```

This prepares the application for:

* multiple users;
* multiple save-data types;
* indexed/cache save data;
* device/system data;
* future emulator-specific edge cases.

---

# 25. Multiple users

`FsSaveDataAttribute` contains an `AccountUid`, and libnx describes it as the user-specific account identifier used when accessing user-specific save data.[2]

Therefore the same application can conceptually have account saves associated with different users.

The normalized identity of a save may involve several values depending on its type:

```text
save-data space
save-data type
application/system ID
account UID
save-data index/rank
SaveDataId
```

The physical SaveDataId remains a distinct container identifier.

---

# 26. Backup boundary

For safety, the generic backup engine should treat the **entire physical save container** as the minimum default snapshot boundary.

Given:

```text
<SaveDataId>/
├── 0/
├── 1/
├── ExtraData0
├── ExtraData1
└── <other entries>
```

the backup system should preserve the entire container recursively.

It must not ask a game plugin which payload file is "important" and then back up only that file.

For example, an NSMBU Deluxe plugin may eventually edit:

```text
rp_savedata.dat
```

but that does not imply that `rp_savedata.dat` is a complete Ryujinx save-data backup.

This is a **RyujinxSaveManager safety policy**, derived from the fact that payloads can contain arbitrary directory trees and that Ryujinx maintains transaction/metadata state around them.[4][5]

---

# 27. Unknown entries

The storage provider follows a preserve-first policy.

If a container contains an unfamiliar entry, the application must not automatically delete, rewrite, or normalize it.

The scanner may report it diagnostically.

Backups should preserve unknown regular entries unless there is a specifically documented reason not to.

This follows the project's general rule:

> Unknown data is preserved, not normalized.

---

# 28. Symbolic links

The discovery scanner does not follow symbolic links inside candidate save containers.

This protects against:

* escaping the selected root;
* recursive cycles;
* unexpectedly backing up unrelated filesystem trees;
* writes reaching outside the intended save container.

A symbolic link encountered during shallow discovery should produce a diagnostic rather than being silently traversed. The current scanner checks immediate container entries; it does not inspect nested payload trees. A future backup or write service must independently reject links anywhere it would traverse.

This is a **RyujinxSaveManager safety policy**, not a claim that Ryujinx itself universally forbids symbolic links.

---

# 29. Current scanner behavior

The initial `RyujinxStorageProvider` scans immediate children of a caller-provided user-save root.

Conceptually:

```text
save/
├── <candidate container>/
├── <candidate container>/
└── ...
```

A candidate container is recognized using conservative structural evidence.

Expected immediate entries may include:

```text
0/
1/
ExtraData0
ExtraData1
```

but not every entry must necessarily be present for discovery.

A directory showing evidence of the directory-save layout may still be reported when incomplete. A canonical 16-digit hexadecimal directory is also kept visible even if none of the expected children remain; missing payload and metadata are reported diagnostically. A noncanonical directory with no structural evidence is not reported as a save.

This is intentional: damaged, interrupted, or historical saves are particularly important not to hide.

---

# 30. Container-name validation

Historical Ryujinx formats user save paths with:

```text
{saveDataId:x16}
```

giving a 16-character lowercase hexadecimal representation of SaveDataId.[1]

The scanner may recognize this canonical form.

However, a malformed or unusual name should be handled diagnostically rather than interpreted as an Application ID.

For example:

```text
0000000000000003
```

means, in this path context:

```text
SaveDataId = 3
```

not:

```text
Title ID = 0000000000000003
```

---

# 31. Current bank discovery

The current helper:

```python
_get_bank_names(...)
```

may identify which of:

```text
0
1
```

exist as real directories.

Documentation and code terminology may describe them as transaction directories/banks with historically confirmed roles:

```text
0 = committed
1 = working
```

for the referenced Ryujinx implementation.[1]

Presence alone does not establish that the contents are valid or that Ryujinx is currently using that tree.

Structural discovery must remain separate from transaction-state interpretation.

---

# 32. Current metadata discovery

Likewise:

```python
_get_metadata_names(...)
```

may report which of:

```text
ExtraData0
ExtraData1
```

exist as regular files.

Metadata parsing should be a separate operation from structural discovery.

A future flow may resemble:

```text
discover container
        ↓
inspect ExtraData candidates
        ↓
validate SaveDataExtraData
        ↓
derive normalized metadata
        ↓
assign confidence / diagnostics
```

This prevents filesystem discovery from becoming dependent on successful metadata interpretation.

---

# 33. Metadata validation strategy

The current read-only header inspection checks size and compares identity fields.
A fuller `SaveDataExtraData` parser should be deliberately strict.

Possible validation inputs include:

```text
file length == 0x200
save-data type (retain unrecognized numeric values)
structurally plausible rank/index
known padding/reserved expectations where applicable
ApplicationId rules for account saves
SystemSaveDataId rules for system saves
consistency between metadata copies
```

The `0x200` size and member structure are supported by libnx.[2]

Validation should return structured results rather than merely a boolean where useful.

For example:

```text
VALID
LEGACY_OR_INCOMPLETE
CONFLICTING_COPIES
UNSUPPORTED_TYPE
MALFORMED
UNKNOWN
```

Current discovery uses size and identity agreement rather than claiming full
semantic validation of every field. Richer validation states remain future work.

---

# 34. Identification confidence

Game identification should carry explicit confidence.

For example:

```text
CONFIRMED
HIGH
TENTATIVE
UNKNOWN
```

Potential evidence may include:

* validated ApplicationId from save metadata;
* agreement between available metadata copies;
* a trusted title database;
* plugin registration;
* plugin-specific structural evidence.

Filename guesses or SaveDataId values must not be promoted into confident game identification.

If metadata is incomplete, the UI should say so.

---

# 35. Display-name resolution

`SaveDataExtraData` can contain an Application ID.[2]

It does not provide a friendly game name such as:

```text
New Super Mario Bros. U Deluxe
```

Display-name resolution is a separate concern.

Possible future sources include:

* Ryujinx application metadata;
* an installed-game library;
* a bundled or downloaded title database;
* plugin registration;
* user-provided labels.

Therefore:

```text
ApplicationId known
```

does not imply:

```text
display_name known
```

The storage parser should not mix those responsibilities.

---

# 36. Filesystem timestamps

Host filesystem timestamps are operational filesystem metadata, not authoritative save transaction state.

Do not infer:

```text
latest host mtime == authoritative save
```

because:

* copying/restoring files can change mtimes;
* filesystem implementations differ;
* WSL may access a Windows-hosted filesystem;
* save metadata includes explicit timestamp and commit information.[2]

Host modification times may be displayed as host filesystem information, but they must be labeled accordingly.

---

# 37. WSL considerations

WSL is the primary development environment.

A Windows Ryujinx installation may be inspected through:

```text
/mnt/c/...
```

Code must therefore not assume that:

```text
Python running on Linux
```

necessarily means:

```text
save tree has ordinary native-Linux filesystem behavior
```

Code dealing with:

* atomic replacement;
* locking;
* case sensitivity;
* rename behavior;
* permissions;
* symlinks;
* timestamps

must be tested across supported Windows and Linux environments.

Use `pathlib.Path` and explicit filesystem operations rather than manually constructing platform-specific separators.

---

# 38. Read safety

Discovery is read-only.

The scanner must not:

* create missing `0` or `1` directories;
* repair metadata;
* copy one bank over another;
* delete lock files;
* update timestamps;
* normalize names;
* write identification information into save containers.

This differs intentionally from Ryujinx's own historical "open save directory" helper, which could create a missing working directory.[1]

RyujinxSaveManager is an external inspection/editing tool, so discovery should have no such side effect.

Malformed containers are reported, not repaired.

---

# 39. Write safety

Future save editing should not mutate arbitrary live paths directly.

The intended application-level model is:

```text
physical save container
        ↓
validate
        ↓
verified backup
        ↓
prepare intended game-data changes
        ↓
game plugin modification
        ↓
game-specific integrity/checksum repair
        ↓
validate expected changes
        ↓
controlled replacement
        ↓
reopen and validate
```

Ryujinx/LibHac transaction metadata must not be rewritten unless the application understands the required semantics.

For ordinary game-level edits, it may be sufficient to modify game payload data within the authoritative mounted representation while Ryujinx is not using it, but that behavior must be experimentally verified before becoming project policy.

---

# 40. Restoration safety

Restoring a Ryujinx save is not necessarily equivalent to replacing one arbitrary game file.

Potentially relevant state includes:

```text
0/
1/
ExtraData0
ExtraData1
user/saveMeta/<SaveDataId>
save-data index state
```

Historical Ryujinx evidence confirms the existence of `saveMeta` and save-index state outside the game payload.[3][7]

The exact boundary required for completely faithful reconstruction still needs investigation.

Until then, the application should distinguish guarantees such as:

```text
restore payload/container of an existing save
```

from:

```text
reconstruct/import an entirely absent Ryujinx save-data object
```

if those operations require different emulator metadata.

---

# 41. Known historical evolution

Ryujinx's save implementation has evolved.

The 2021 update to LibHac 0.13.1 included:

* storage of `SaveDataExtraData` for directory save data;
* directory locking;
* more accurate filesystem service behavior;
* recreation of missing save extra data;
* repair/indexing of certain historical system saves.[5]

This establishes that save trees created by different Ryujinx/LibHac versions may differ in metadata completeness.

The scanner should therefore be:

```text
tolerant during discovery
strict before interpretation
very strict before modification
```

---

# 42. Practical conceptual model

RyujinxSaveManager should use a model conceptually similar to:

```text
RyujinxSaveRoot
│
├── SaveDataContainer
│   ├── save_data_id
│   ├── save_data_space
│   ├── metadata
│   │   ├── application_id
│   │   ├── account_uid
│   │   ├── system_save_data_id
│   │   ├── save_data_type
│   │   ├── save_data_rank
│   │   ├── save_data_index
│   │   ├── owner_id
│   │   ├── timestamp
│   │   ├── flags
│   │   ├── data_size
│   │   ├── journal_size
│   │   ├── commit_id
│   │   └── ...
│   │
│   ├── committed filesystem (0)
│   ├── working filesystem (1)
│   ├── ExtraData0
│   ├── ExtraData1
│   └── unknown/preserved entries
│
└── SaveDataContainer
    └── ...
```

Then the application layer may associate one or more containers with an application/game:

```text
Game
├── ApplicationId
├── DisplayName
├── Plugin
└── SaveDataContainer(s)
```

This prevents the architectural mistake of treating a physical Ryujinx directory as synonymous with a game.

---

# 43. Current `DiscoveredSave` behavior

The scanner records a canonical 16-digit physical SaveDataId only when the
container name has that form. It checks each `ExtraData` file is exactly
`0x200` bytes and compares Application ID, AccountUid, SystemSaveDataId, and
save-data type across copies. With two agreeing copies, it exposes a nonzero
Application ID in `title_id` as 16 uppercase hexadecimal digits and the save
type through the provider-neutral `SaveType` value (original numeric code and
display label), including Account, Device, and BCAT. The Switch-specific
`SaveDataType` enum remains inside the Ryujinx storage package. Unknown
numeric save types retain their original code and do not crash discovery. A zero
Application ID stays unidentified. A single copy or a malformed copy does not
establish identity under the current conservative policy. Disagreement produces
`CONFLICTING_METADATA`; the scanner does not select a winner.

**Source evidence:** libnx defines field offsets and type values.[2] Original
Ryujinx source documents the directory structure and metadata storage at the
referenced commits.[1][5] **Observed evidence:** three real Ryujinx containers
were inspected read-only: container A had Application ID `01006F8002326000`
and type Device; container B had the same Application ID and type BCAT;
container C had Application ID `0100EA80032EA000` and type Account. Their
metadata copies agreed on the inspected identity fields. The AccountUid was
zero in the observed Device and BCAT records and nonzero in the Account record;
its full user-facing representation is not yet established. No personal path,
AccountUid value, or real metadata file is committed. Repository tests use
synthetic bytes. **Confidence: HIGH CONFIDENCE for observed serialization;
UNKNOWN for transaction-bank authority and broad fork/version behavior.**

Fields such as:

```text
user_id
display_name
```

remain `None`; `title_id` and `save_data_type` may also remain `None` when
evidence is insufficient. `save_data_id` is never inferred from the metadata
Application ID.

The UI should present:

```text
SaveDataId 0000000000000001 · Application ID: 01006F8002326000 · Save type: Device
```

rather than guessing a friendly game name.

`display_name` remains a separate resolution problem.

---

# 44. Diagnostics

Discovery diagnostics should use stable `DiscoveryDiagnosticCode` values.

Useful diagnostic categories may eventually include:

```text
NON_CANONICAL_CONTAINER_NAME
MISSING_COMMITTED_BANK
MISSING_WORKING_BANK
MISSING_EXTRA_DATA
INVALID_EXTRA_DATA_SIZE
EXTRA_DATA_CONFLICT
UNSUPPORTED_SAVE_DATA_TYPE
SYMLINK_SKIPPED
UNKNOWN_CONTAINER_ENTRY
FILESYSTEM_ERROR
LOCK_PRESENT
```

These names are illustrative; existing public codes should not be renamed without reason.

The enum should own generic user-facing messages.

Provider code should primarily select diagnostic codes and attach contextual details.

Diagnostics are observations, not automatic repair instructions.

---

# 45. Backup policy derived from this model

The storage research leads to the following project safety rules:

1. Never assume the file edited by a game plugin is the complete save.
2. Snapshot the whole physical save container by default.
3. Preserve both `0` and `1` when present.
4. Preserve both `ExtraData` files when present.
5. Preserve unknown regular entries.
6. Never follow arbitrary symbolic links.
7. Record hashes for backed-up regular files.
8. Record SaveDataId separately from ApplicationId.
9. Record parsed metadata separately from its original raw bytes.
10. Never modify a completed backup.
11. Treat related `saveMeta` state separately until its restoration role is understood.
12. Do not claim that a backup can reconstruct a completely absent Ryujinx save unless that process has been verified.

These are RyujinxSaveManager policies rather than claims about the internal behavior of Ryujinx itself.

---

# 46. Research still required

The following questions remain important before full write/restore support.

## Transaction algorithm

Verify against the LibHac versions used by supported Ryujinx/Ryubing builds:

* precise commit sequence between `0` and `1`;
* precise relationship between `ExtraData0` and `ExtraData1`;
* recovery behavior after interruption at each commit stage;
* how `commit_id` participates in transaction state;
* whether both directories normally exist after clean shutdown;
* when either directory may legitimately be absent.

## Metadata

Verify with fixtures:

* serialized endianness of fields beyond the observed little-endian Application ID;
* exact AccountUid representation;
* save-data types encountered in real user save roots;
* differences between user and system metadata;
* legacy metadata behavior;
* behavior when `ExtraData0` and `ExtraData1` disagree.

## Save index and `saveMeta`

Determine:

* exact format and purpose of `bis/user/saveMeta`;
* current relationship between `saveMeta`, the save-data indexer, and physical containers;
* whether replacing an existing `bis/user/save/<SaveDataId>` container is sufficient for restoration;
* what is required to import a save-data object that does not already exist in the emulator's index.

## Locking

Determine:

* current on-disk lock behavior;
* reliable detection that Ryujinx is using a container;
* whether read-only inspection while mounted is safe;
* whether writes should be completely prohibited while Ryujinx is running.

## Fork compatibility

Test against representative versions of:

* historical Ryujinx;
* Ryujinx Canary builds relevant to this project;
* current Ryubing;
* portable installations;
* Windows;
* Linux;
* Windows save trees accessed from WSL.

These should become fixture-backed observations rather than assumptions.

---

# 47. Evidence hierarchy

When researching storage behavior, prefer evidence in this order:

1. source code for the relevant Ryujinx/Ryubing version;
2. source code for the LibHac version used by it;
3. libnx / Switch filesystem structure definitions;
4. reproducible fixtures from actual emulator installations;
5. independent tooling that parses Ryujinx saves;
6. emulator documentation;
7. issue reports and community observations.

Community reports are useful evidence of real-world filesystem states but should not define binary semantics by themselves.

When new behavior is discovered, document:

```text
source/version
platform
observed tree
expected behavior
actual behavior
confidence
```

before converting the observation into scanner or writer logic.

---

# 48. Core invariant

The storage provider must always distinguish between:

```text
what exists physically
```

and:

```text
what we believe it means
```

Discovery may be permissive.

Interpretation must be evidence-based.

Writing must be strict.

When uncertain, preserve the data and report the uncertainty rather than guessing.

---

# References

[1]: Ryujinx, `ApplicationHelper.OpenSaveDir`, historical source at commit `d6d3cdd5739e6b8f8df36bf393e440f4857fb2b7`. The implementation constructs `user/save/{saveDataId:x16}`, names `<container>/0` the committed path and `<container>/1` the working path, and documents which path will be loaded on the next save-data mount.
https://git.axenov.dev/Museum/ryujinx/src/commit/d6d3cdd5739e6b8f8df36bf393e440f4857fb2b7/src/Ryujinx.Ava/Common/ApplicationHelper.cs

[2]: switchbrew/libnx, `nx/include/switch/services/fs.h`. Defines `FsSaveDataSpaceId`, `FsSaveDataType`, `FsSaveDataAttribute`, `FsSaveDataExtraData`, `FsSaveDataInfo`, and the public save-data filesystem operations.
https://github.com/switchbrew/libnx/blob/master/nx/include/switch/services/fs.h

[3]: Ryujinx, `VirtualFileSystem.cs`, historical source at commit `356e480bf55d9a1497fcf54e9395d9b8ab72b815`. Contains system-save enumeration and repair logic for save directories, save-data indexing, and missing/invalid extra data.
https://git.axenov.dev/Museum/ryujinx/src/commit/356e480bf55d9a1497fcf54e9395d9b8ab72b815/Ryujinx.HLE/FileSystem/VirtualFileSystem.cs

[4]: Ryubing Issues #201, user-observed save layout for Inazuma Eleven: Victory Road. Reports `0`, `1`, `ExtraData0`, and `ExtraData1` and game-defined `SYSTEM`, `HEADERSAVE`, and `AUTOSAVE` directories. This is observational evidence, not a format specification.
https://github.com/Ryubing/Issues/issues/201

[5]: Ryujinx commit `19afb3209c48db5f8e4b5f48f0faee925cd20d9f`, "Update to LibHac 0.13.1 (#2328)". The change description documents directory-save `SaveDataExtraData` storage, directory locking, recreation of missing extra data, and repair/indexing of older system saves.
https://git.axenov.dev/Museum/ryujinx/commit/19afb3209c48db5f8e4b5f48f0faee925cd20d9f

[6]: Junohea/SESS, Switch Emulator Save Sync. Its documented scanner reads Ryujinx `portable/bis/user/save/<hex>` directories and extracts a Title ID from `ExtraData0`. This is independent-tool evidence and should not override Ryujinx/LibHac definitions.
https://github.com/Junohea/SESS

[7]: Ryujinx commit `19afb3209c48db5f8e4b5f48f0faee925cd20d9f`, historical user-save deletion code. It constructs both `user/save/<SaveDataId>` and `user/saveMeta/<SaveDataId>` and removes both.
https://git.axenov.dev/Museum/ryujinx/commit/19afb3209c48db5f8e4b5f48f0faee925cd20d9f

---

# Third-party and research note

This document describes interoperability information, publicly documented filesystem structures, and behavior observed in emulator implementations.

Ryujinx, Ryubing, LibHac, libnx, Nintendo Switch, Nintendo, and game names and identifiers referenced by this project remain associated with their respective authors or rights holders.

References to third-party projects are provided as technical sources. Their source code, documentation, assets, and licenses remain separate from RyujinxSaveManager's MIT-licensed original code and documentation unless explicitly stated otherwise.

Technical conclusions derived from historical source should retain enough source/version information to make clear which implementation was actually examined.
