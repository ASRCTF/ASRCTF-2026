using UnityEngine;

public class GoofyNotebook : Item {
    public string[] arr;
    bool open = false;
    bool firstOpen = true;

    void Update() {
        if (!firstOpen) return;
        if (ItemManager.hotbarItems[ItemManager.hotbarSlot] == null) return;
        if (ItemManager.hotbarItems[ItemManager.hotbarSlot].GetComponent<Item>().ID != ID) return;

        if (Input.GetMouseButtonDown(0)) {
            open = !open;

            if (!open) {
                firstOpen = false;
                MenuManager.instance.GUI.SetActive(false);
                Player.shared.theCollider.enabled = false;
                Player.shared.shouldClip = false;
                Player.shared.controller.detectCollisions = false;
                MenuManager.allowTeleport = true;
                
            } else {
                MenuManager.instance.GUI.SetActive(true);
            }
        }
    }
}
