import argparse
import json
from xml.etree import ElementTree as ET
from xml.dom import minidom
from type_declarations import *


def convert_json_to_xml(json_file, xml_file):
    with open(json_file, "r") as f:
        json_checklist: JsonFile = json.load(f)

    root = ET.Element("Checklist")
    if "defaultChecklist" in json_checklist:
        root.set("default-group-index", str(json_checklist["defaultChecklist"]["group"]))
        root.set("default-list-index", str(json_checklist["defaultChecklist"]["checklist"]))

    for group in json_checklist["groups"]:
        group_element = ET.SubElement(root, "Group")
        group_element.set("name", group["name"])
        for checklist in group["checklists"]:
            list_element = ET.SubElement(group_element, "List")
            list_element.set("name", checklist["name"])
            list_element.set("uid", get_list_uid(group["name"], checklist["name"]))
            for entry in checklist["entries"]:
                item_element = get_item_element(entry, json_checklist)
                list_element.append(item_element)

                # Add optional spacer element
                if "blanksBelow" in entry:
                    list_element.append(get_spacer_element(entry))

                # Add branch sub-checklists if they exist
                if "branches" in entry:
                    for branch_index in entry["branches"]:
                        json_branch = json_checklist["branchChecklists"][branch_index]

                        branch_element = ET.SubElement(list_element, "Branch")
                        branch_element.set("uid", f"{branch_index}-"+json_branch["name"].replace(' ', '-').lower())
                        branch_element.set("name", json_branch["name"])
                        for branch_entry in json_branch["entries"]:
                            branch_item_element = get_item_element(branch_entry, json_checklist)
                            branch_element.append(branch_item_element)

                            # Add optional spacer element
                            if "blanksBelow" in entry:
                                list_element.append(get_spacer_element(entry))


    xml_str = ET.tostring(root, encoding="unicode")
    xml_str = minidom.parseString(xml_str).toprettyxml(indent="    ")
    with open(xml_file, "w") as f:
        f.write(xml_str)


def get_list_uid(group_name: str, list_name:str) -> str:
    return f"{group_name}-{list_name}".replace(' ', '-').lower()


def get_item_element(entry: JsonEntry, json_checklist: JsonFile) -> ET.Element:
    entry_type = next(entry_type for entry_type in json_checklist["entryTypes"] if entry_type["name"] == entry["type"])

    item_element = ET.Element("Item")

    # Set the type of the item
    if entry_type["interaction"] == "checkbox":
        item_element.set("type", ItemType.Actionable.value)
    elif entry_type["interaction"] == "branchParent":
        item_element.set("type", ItemType.Branch.value)
    elif entry_type["interaction"] == "link":
        item_element.set("type", ItemType.Link.value)
    elif entry_type["interaction"] == "scrollStop":
        item_element.set("type", ItemType.Note.value)
    elif entry_type["interaction"] == "noScrollStop":
        item_element.set("type", ItemType.Title.value)
    else:
        raise ValueError(f"Unknown interaction type '{entry_type['interaction']}'")

    # Set the color of the item if not default
    if entry_type["color"] != "white" or (entry_type["color"] == "cyan" and entry_type["interaction"] != "link" and entry_type["interaction"] != "branchParent"):
        item_element.set("color", entry_type["color"])

    # Set the indentation if specified
    if "justification" in entry:
        if entry["justification"].startswith("indent"):
            item_element.set("indent", entry["justification"][-1])
        else:
            item_element.set("justification", entry["justification"])

    # Set the item content
    if item_element.get("type") == ItemType.Actionable.value:
        label_text = ET.SubElement(item_element, "LabelText")
        label_text.text = entry["text"].replace("\n", "\\n")
        if "response" in entry:
            action_text = ET.SubElement(item_element, "ActionText")
            action_text.text = entry["response"].replace("\n", "\\n")
            item_element.append(action_text)
    elif item_element.get("type") == ItemType.Branch.value:
        uid = entry["text"].replace(' ', '-').lower()
        item_element.set("uid", uid)
        item_element.set("auto-link", "true")
        if "hideParentCheckbox" in entry and entry["hideParentCheckbox"]:
            item_element.set("omit-checkbox", "true")
        for branch_index in entry["branches"]:
            json_branch = json_checklist["branchChecklists"][branch_index]
            branch_element = ET.SubElement(item_element, "Branch")
            branch_element.set("logic", "sufficient")
            branch_uid = f"{branch_index}-"+json_branch["name"].replace(' ', '-').lower()
            branch_element.text = branch_uid
        text_element = ET.SubElement(item_element, "Text")
        text_element.text = entry["text"].replace("\n", "\\n")
    elif item_element.get("type") == ItemType.Link.value:
        target_element = ET.SubElement(item_element, "Target")
        uid = get_list_uid(json_checklist["groups"][entry["linkedChecklist"]["group"]]["name"],
                           json_checklist["groups"][entry["linkedChecklist"]["group"]]["checklists"][entry["linkedChecklist"]["checklist"]]["name"])
        target_element.text = uid
        text_element = ET.SubElement(item_element, "Text")
        text_element.text = entry["text"].replace("\n", "\\n")
    elif item_element.get("type") == ItemType.Note.value or item_element.get("type") == ItemType.Title.value:
        note_text = ET.SubElement(item_element, "Text")
        note_text.text = entry["text"].replace("\n", "\\n")

    return item_element


def get_spacer_element(entry) -> ET.Element:
    spacer_element = ET.Element("Item")
    spacer_element.set("type", ItemType.Spacer.value)
    spacer_element.set("height", str(entry["blanksBelow"]))
    return spacer_element


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Garmin checklist JSON to Avionics Framework XML checklist.")
    parser.add_argument("json_file", help="Path to the input JSON file.")
    parser.add_argument("xml_file", help="Path to the output XML file.")
    args = parser.parse_args()

    convert_json_to_xml(args.json_file, args.xml_file)
    print(f"Checklist conversion complete. XML file created at '{args.xml_file}'")
