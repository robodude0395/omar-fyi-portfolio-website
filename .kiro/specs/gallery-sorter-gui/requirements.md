# Requirements Document

## Introduction

The Gallery Sorter is a standalone graphical utility tool that lets the user visually browse all media files (images and videos) in a specific subfolder under `frontend/public/media/`, accept or reject each file for inclusion, write descriptions, and output a `gallery.json` manifest. This replaces the manual process of editing `gallery.json` by hand without knowing what each cryptically-named file looks like.

## Glossary

- **Gallery_Sorter**: The standalone graphical desktop application that displays media files and produces a Gallery_Manifest
- **Gallery_Manifest**: A `gallery.json` file located in a Media_Folder, containing a JSON array of objects each with a `file` (string) and `description` (string) field
- **Media_Folder**: A subdirectory under `frontend/public/media/` containing media files for a specific blog post
- **Media_File**: An image or video file with a supported extension (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.mp4`, `.webm`)
- **Accepted_File**: A Media_File that the user has chosen to include in the Gallery_Manifest
- **Rejected_File**: A Media_File that the user has chosen to exclude from the Gallery_Manifest
- **Description_Field**: A text input where the user writes a one-line caption for an Accepted_File

## Requirements

### Requirement 1: Launch and Folder Selection

**User Story:** As a blog author, I want to launch the Gallery Sorter and select a media folder, so that I can begin sorting media for a specific blog post.

#### Acceptance Criteria

1. THE Gallery_Sorter SHALL be launchable from the command line with an optional folder name argument
2. WHEN launched without a folder name argument, THE Gallery_Sorter SHALL display a folder selection mechanism allowing the user to choose a Media_Folder from the available subdirectories under `frontend/public/media/`
3. WHEN launched with a folder name argument, THE Gallery_Sorter SHALL open directly to that Media_Folder
4. IF the specified folder name does not exist under `frontend/public/media/`, THEN THE Gallery_Sorter SHALL display an error message and exit
5. WHEN a Media_Folder is selected, THE Gallery_Sorter SHALL scan the folder for all files matching supported extensions (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.mp4`, `.webm`)
6. IF the selected Media_Folder contains zero Media_Files, THEN THE Gallery_Sorter SHALL display a message indicating no supported media files were found and exit

### Requirement 2: Media Display and Navigation

**User Story:** As a blog author, I want to visually flip through media files one at a time, so that I can see what each file looks like before deciding to include it.

#### Acceptance Criteria

1. WHEN a Media_Folder is loaded, THE Gallery_Sorter SHALL display the first Media_File in the folder
2. THE Gallery_Sorter SHALL display image files (`.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`) as rendered images scaled to fit the display area
3. THE Gallery_Sorter SHALL display video files (`.mp4`, `.webm`) as a playable video player or a representative thumbnail frame
4. THE Gallery_Sorter SHALL display the current Media_File filename below or above the media preview
5. THE Gallery_Sorter SHALL display a progress indicator showing the current file index and total file count (e.g., "3 / 15")
6. WHEN the user navigates forward, THE Gallery_Sorter SHALL display the next Media_File in the sequence
7. WHEN the user navigates backward, THE Gallery_Sorter SHALL display the previous Media_File in the sequence
8. WHILE the user is on the first Media_File, THE Gallery_Sorter SHALL disable backward navigation
9. WHILE the user is on the last Media_File, THE Gallery_Sorter SHALL disable forward navigation

### Requirement 3: Accept and Reject Media Files

**User Story:** As a blog author, I want to accept or reject each media file, so that only the files I choose end up in the gallery manifest.

#### Acceptance Criteria

1. THE Gallery_Sorter SHALL provide an "Accept" action for the currently displayed Media_File
2. THE Gallery_Sorter SHALL provide a "Reject" action for the currently displayed Media_File
3. WHEN the user accepts a Media_File, THE Gallery_Sorter SHALL mark the file as an Accepted_File and advance to the next Media_File
4. WHEN the user rejects a Media_File, THE Gallery_Sorter SHALL mark the file as a Rejected_File and advance to the next Media_File
5. THE Gallery_Sorter SHALL visually indicate whether a previously visited Media_File was accepted or rejected when the user navigates back to the file
6. WHEN the user navigates back to a previously accepted or rejected Media_File, THE Gallery_Sorter SHALL allow the user to change the decision

### Requirement 4: Description Entry

**User Story:** As a blog author, I want to write a description for each accepted media file, so that the gallery displays meaningful captions.

#### Acceptance Criteria

1. WHEN the user accepts a Media_File, THE Gallery_Sorter SHALL display a Description_Field for the user to enter a one-line caption
2. THE Gallery_Sorter SHALL allow the Description_Field to be left empty (resulting in an empty string in the Gallery_Manifest)
3. WHEN the user navigates back to an Accepted_File, THE Gallery_Sorter SHALL display the previously entered description in the Description_Field
4. THE Gallery_Sorter SHALL allow the user to edit the description of any Accepted_File at any time before saving

### Requirement 5: Gallery Manifest Output

**User Story:** As a blog author, I want the tool to output a valid gallery.json file, so that my blog post gallery works correctly.

#### Acceptance Criteria

1. THE Gallery_Sorter SHALL provide a "Save" action to write the Gallery_Manifest
2. WHEN the user triggers the Save action, THE Gallery_Sorter SHALL write a `gallery.json` file to the selected Media_Folder
3. THE Gallery_Sorter SHALL write the Gallery_Manifest as a JSON array of objects, each containing a `file` field (string) and a `description` field (string)
4. THE Gallery_Sorter SHALL include only Accepted_Files in the Gallery_Manifest
5. THE Gallery_Sorter SHALL preserve the order in which files were accepted in the Gallery_Manifest
6. THE Gallery_Sorter SHALL format the output JSON with 2-space indentation and a trailing newline
7. IF a `gallery.json` file already exists in the Media_Folder, THEN THE Gallery_Sorter SHALL prompt the user for confirmation before overwriting

### Requirement 6: Existing Manifest Loading

**User Story:** As a blog author, I want the tool to load an existing gallery.json so that I can edit a previously created manifest without starting from scratch.

#### Acceptance Criteria

1. WHEN a Media_Folder containing an existing `gallery.json` is opened, THE Gallery_Sorter SHALL parse the existing Gallery_Manifest
2. WHEN an existing Gallery_Manifest is loaded, THE Gallery_Sorter SHALL pre-mark files listed in the manifest as Accepted_Files
3. WHEN an existing Gallery_Manifest is loaded, THE Gallery_Sorter SHALL pre-populate the Description_Field for each Accepted_File with the description from the manifest
4. WHEN an existing Gallery_Manifest is loaded, THE Gallery_Sorter SHALL pre-mark files present in the Media_Folder but absent from the manifest as Rejected_Files
5. IF the existing `gallery.json` contains entries referencing files that no longer exist in the Media_Folder, THEN THE Gallery_Sorter SHALL ignore those entries and display a warning

### Requirement 7: Keyboard Shortcuts

**User Story:** As a blog author, I want keyboard shortcuts for common actions, so that I can sort through media files quickly.

#### Acceptance Criteria

1. THE Gallery_Sorter SHALL support a keyboard shortcut for the Accept action
2. THE Gallery_Sorter SHALL support a keyboard shortcut for the Reject action
3. THE Gallery_Sorter SHALL support keyboard shortcuts for navigating to the next and previous Media_File
4. THE Gallery_Sorter SHALL display the available keyboard shortcuts in the interface

### Requirement 8: Documentation

**User Story:** As a developer, I want a quick-start guide in the root README and full documentation alongside the tool, so that I can find usage info in the right place.

#### Acceptance Criteria

1. THE root README.md SHALL contain a brief section (no more than a few paragraphs) describing the Gallery_Sorter tool's purpose and basic usage command
2. THE root README.md section SHALL direct the reader to the full documentation located alongside the Gallery_Sorter tool
3. THE Gallery_Sorter's own directory SHALL contain a dedicated README.md with full documentation including command-line usage, all features, keyboard shortcuts, dependencies, and configuration details

### Requirement 9: Gallery Manifest Serialization Round-Trip

**User Story:** As a blog author, I want confidence that loading and saving a gallery.json preserves my data exactly.

#### Acceptance Criteria

1. FOR ALL valid Gallery_Manifest files, loading the manifest into the Gallery_Sorter and saving without modifications SHALL produce a file with equivalent JSON content to the original
