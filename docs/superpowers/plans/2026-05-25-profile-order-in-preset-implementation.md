# Profile Order In Preset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a separate `Порядок в preset` page that shows only real profile blocks from the selected preset and lets drag/drop rewrite their order inside the preset file.

**Architecture:** Keep the current grouped preset setup page unchanged as the default view. Add a separate hidden nested page for preset order, a direct service payload built from `preset.profiles`, and service methods that use the existing preset serializer to move profile blocks in the `.txt` file.

**Tech Stack:** PyQt6, qfluentwidgets, existing ZapretGUI page registry, `ProfilePresetService`, `ProfileListItem`, `with_profile_moved`, focused unittest contract tests.

---

### Task 1: Service Contract

**Files:**
- Modify: `src/profile/service.py`
- Modify: `src/profile/commands.py`
- Modify: `src/app/feature_facades/profile.py`
- Test: `tests/test_profile_list_payload.py`

- [ ] **Step 1: Write failing tests**

Add tests that prove the order payload uses raw `preset.profiles`, excludes template-only rows, preserves duplicate resources, and that moving a profile rewrites the preset order instead of `settings.json`.

- [ ] **Step 2: Run red tests**

Run: `PYTHONPATH=src python -m unittest tests.test_profile_list_payload`

- [ ] **Step 3: Implement service methods**

Add `list_preset_order_profiles()`, `move_preset_profile_before()`, `move_preset_profile_after()`, and `move_preset_profile_to_end()` on `ProfilePresetService`. Wire them through `profile.commands` and `ProfileFeature`.

- [ ] **Step 4: Run green tests**

Run: `PYTHONPATH=src python -m unittest tests.test_profile_list_payload`

### Task 2: Flat Order UI

**Files:**
- Create: `src/profile/ui/profile_order_list.py`
- Create: `src/profile/ui/profile_order_page.py`
- Modify: `src/profile/ui/shell.py`
- Modify: `src/profile/ui/preset_setup_page.py`
- Test: `tests/test_profile_order_page.py`
- Test: `tests/test_profile_setup_page_contract.py`

- [ ] **Step 1: Write failing UI contract tests**

Add tests that assert the shell has a `Порядок в preset` button, the normal setup page routes through `open_profile_order`, and the order page uses a flat list with no folder/context actions.

- [ ] **Step 2: Run red tests**

Run: `PYTHONPATH=src python -m unittest tests.test_profile_order_page tests.test_profile_setup_page_contract`

- [ ] **Step 3: Implement widgets**

Build `ProfileOrderList` on top of `ProfileListView` and `ProfileListDelegate`, but with a flat model that only emits profile rows. Build `ProfileOrderPageBase` with breadcrumbs, priority text, reload-on-activate, and drag/drop handlers that call the new service methods then reload from file.

- [ ] **Step 4: Add toolbar entry**

Add `Порядок в preset` as a separate button on the existing preset setup toolbar. Do not add explanatory text to the default grouped page.

- [ ] **Step 5: Run green tests**

Run: `PYTHONPATH=src python -m unittest tests.test_profile_order_page tests.test_profile_setup_page_contract`

### Task 3: Navigation Wiring

**Files:**
- Modify: `src/app/page_names.py`
- Modify: `src/ui/navigation/schema.py`
- Modify: `src/ui/navigation_pages.py`
- Modify: `src/ui/page_deps/presets.py`
- Modify: `src/ui/page_composition.py`
- Modify: `src/ui/pages/__init__.py`
- Test: `tests/test_preset_sidebar_navigation.py`

- [ ] **Step 1: Write failing navigation tests**

Add assertions that Zapret 1 and Zapret 2 have hidden profile-order pages under their preset setup pages and that the preset setup page receives `open_profile_order`.

- [ ] **Step 2: Run red tests**

Run: `PYTHONPATH=src python -m unittest tests.test_preset_sidebar_navigation`

- [ ] **Step 3: Wire pages**

Add `ZAPRET2_PROFILE_ORDER` and `ZAPRET1_PROFILE_ORDER`, route specs, navigation resolvers, page deps builders, and lazy exports.

- [ ] **Step 4: Run green tests**

Run: `PYTHONPATH=src python -m unittest tests.test_preset_sidebar_navigation`

### Task 4: Final Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused profile checks**

Run: `PYTHONPATH=src python -m unittest tests.test_profile_list_payload tests.test_profile_order_page tests.test_profile_setup_page_contract tests.test_preset_sidebar_navigation tests.test_profile_drag_indicator`

- [ ] **Step 2: Run architecture checks**

Run: `PYTHONPATH=src python -m app.architecture_checks`

- [ ] **Step 3: Inspect git scope**

Run: `git status --short --untracked-files=all`

Only stage files from this feature. Do not stage the unrelated modified builtin preset.
