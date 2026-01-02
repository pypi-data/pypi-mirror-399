import time

import pytest
from codemie_sdk.models.integration import IntegrationType

from codemie_test_harness.tests import PROJECT, TEST_USER
from codemie_test_harness.tests.utils.constants import test_project_name

DELETION_DELAY = 1
BATCH_DELAY = 2.0
DELETE_CONVERSATIONS = True


def _get_common_filters():
    return {
        "project": [PROJECT, test_project_name],
        "created_by": TEST_USER,
    }


def _delete_integrations(client, integration_type: IntegrationType) -> int:
    type_name = integration_type.value
    print(f"\n🔍 Fetching {type_name} integrations...")

    total_count = 0
    batch_number = 1

    while True:
        integrations = client.integrations.list(
            setting_type=integration_type,
            filters=_get_common_filters(),
            per_page=200,
        )

        batch_count = len(integrations)
        if batch_count == 0:
            if total_count == 0:
                print(f"✓ No {type_name} integrations found")
            else:
                print(f"✓ No more {type_name} integrations found")
            break

        print(
            f"🗑️  Batch {batch_number}: Deleting {batch_count} {type_name} integration(s)..."
        )
        for integration in integrations:
            print(
                f"   - Deleting {type_name} integration: {integration.alias} (ID: {integration.id})"
            )
            client.integrations.delete(
                setting_id=integration.id, setting_type=integration_type
            )
            time.sleep(DELETION_DELAY)

        total_count += batch_count
        batch_number += 1

        if batch_count < 200:
            break

        print(f"   ⏳ Waiting {BATCH_DELAY}s before next batch...")
        time.sleep(BATCH_DELAY)

    if total_count > 0:
        print(
            f"✓ Successfully deleted {total_count} {type_name} integration(s) in {batch_number - 1} batch(es)"
        )
    return total_count


def _delete_datasources(client) -> int:
    print("\n🔍 Fetching datasources...")

    total_count = 0
    batch_number = 1

    while True:
        datasources = client.datasources.list(
            filters=_get_common_filters(),
            per_page=200,
        )

        batch_count = len(datasources)
        if batch_count == 0:
            if total_count == 0:
                print("✓ No datasources found")
            else:
                print("✓ No more datasources found")
            break

        print(f"🗑️  Batch {batch_number}: Deleting {batch_count} datasource(s)...")
        for datasource in datasources:
            print(f"   - Deleting datasource: {datasource.name} (ID: {datasource.id})")
            client.datasources.delete(datasource_id=datasource.id)
            time.sleep(DELETION_DELAY)

        total_count += batch_count
        batch_number += 1

        if batch_count < 200:
            break

        print(f"   ⏳ Waiting {BATCH_DELAY}s before next batch...")
        time.sleep(BATCH_DELAY)

    if total_count > 0:
        print(
            f"✓ Successfully deleted {total_count} datasource(s) in {batch_number - 1} batch(es)"
        )
    return total_count


def _delete_assistants(client) -> tuple[int, int]:
    print("\n🔍 Fetching assistants...")

    total_assistant_count = 0
    total_conversation_count = 0
    batch_number = 1

    while True:
        assistants = client.assistants.list(
            filters=_get_common_filters(),
            per_page=200,
        )

        batch_count = len(assistants)
        if batch_count == 0:
            if total_assistant_count == 0:
                print("✓ No assistants found")
            else:
                print("✓ No more assistants found")
            break

        if DELETE_CONVERSATIONS:
            print(
                f"🗑️  Batch {batch_number}: Deleting {batch_count} assistant(s) and their conversations..."
            )
        else:
            print(f"🗑️  Batch {batch_number}: Deleting {batch_count} assistant(s)...")

        for assistant in assistants:
            print(f"   - Deleting assistant: {assistant.name} (ID: {assistant.id})")
            client.assistants.delete(assistant_id=assistant.id)
            time.sleep(DELETION_DELAY)

            if DELETE_CONVERSATIONS:
                conversations = client.conversations.list_by_assistant_id(assistant.id)
                if conversations:
                    print(
                        f"     └─ Deleting {len(conversations)} conversation(s) for assistant {assistant.id}"
                    )
                    for conversation in conversations:
                        print(f"        - Conversation ID: {conversation.id}")
                        client.conversations.delete(conversation.id)
                        time.sleep(DELETION_DELAY)
                        total_conversation_count += 1

        total_assistant_count += batch_count
        batch_number += 1

        if batch_count < 200:
            break

        print(f"   ⏳ Waiting {BATCH_DELAY}s before next batch...")
        time.sleep(BATCH_DELAY)

    if total_assistant_count > 0:
        if DELETE_CONVERSATIONS:
            print(
                f"✓ Successfully deleted {total_assistant_count} assistant(s) and {total_conversation_count} conversation(s) in {batch_number - 1} batch(es)"
            )
        else:
            print(
                f"✓ Successfully deleted {total_assistant_count} assistant(s) in {batch_number - 1} batch(es) (conversations cascade-deleted)"
            )
    return total_assistant_count, total_conversation_count


def _delete_workflows(client) -> int:
    print("\n🔍 Fetching workflows...")

    total_count = 0
    batch_number = 1

    while True:
        workflows = client.workflows.list(
            filters=_get_common_filters(),
            per_page=200,
        )

        batch_count = len(workflows)
        if batch_count == 0:
            if total_count == 0:
                print("✓ No workflows found")
            else:
                print("✓ No more workflows found")
            break

        print(f"🗑️  Batch {batch_number}: Deleting {batch_count} workflow(s)...")
        for workflow in workflows:
            print(f"   - Deleting workflow: {workflow.name} (ID: {workflow.id})")
            client.workflows.delete(workflow_id=workflow.id)
            time.sleep(DELETION_DELAY)

        total_count += batch_count
        batch_number += 1

        if batch_count < 200:
            break

        print(f"   ⏳ Waiting {BATCH_DELAY}s before next batch...")
        time.sleep(BATCH_DELAY)

    if total_count > 0:
        print(
            f"✓ Successfully deleted {total_count} workflow(s) in {batch_number - 1} batch(es)"
        )
    return total_count


@pytest.mark.clean
@pytest.mark.timeout(600)
def test_clean_all_entities(client):
    print("\n" + "=" * 80)
    print("🧹 CLEANUP: Starting entity cleanup process")
    print("=" * 80)
    print(f"📋 Projects: {PROJECT}, {test_project_name}")
    print(f"👤 User: {TEST_USER}")

    total_deleted = {
        "project_integrations": _delete_integrations(client, IntegrationType.PROJECT),
        "user_integrations": _delete_integrations(client, IntegrationType.USER),
        "datasources": _delete_datasources(client),
        "assistants": (_delete_assistants(client))[0],
        "conversations": (_delete_assistants(client))[1],
        "workflows": _delete_workflows(client),
    }

    print("\n" + "=" * 80)
    print("📊 CLEANUP SUMMARY")
    print("=" * 80)
    print(f"  Project Integrations: {total_deleted['project_integrations']}")
    print(f"  User Integrations:    {total_deleted['user_integrations']}")
    print(f"  Datasources:          {total_deleted['datasources']}")
    print(f"  Assistants:           {total_deleted['assistants']}")
    if DELETE_CONVERSATIONS:
        print(f"  Conversations:        {total_deleted['conversations']}")
    else:
        print(
            f"  Conversations:        {total_deleted['conversations']} (cascade-deleted)"
        )
    print(f"  Workflows:            {total_deleted['workflows']}")
    print("-" * 80)
    total_count = sum(total_deleted.values())
    print(f"  TOTAL ENTITIES:       {total_count}")
    print("=" * 80)
    print("✅ Cleanup completed successfully!\n")
