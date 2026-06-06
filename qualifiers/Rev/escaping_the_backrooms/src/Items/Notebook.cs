using UnityEngine;
public class Notebook : Item {
    void Update() {
        if (ItemManager.hotbarItems[ItemManager.hotbarSlot].GetComponent<Item>().ID != ID)
            return;

        if (Input.GetMouseButtonDown(0)) {
            
        }
    }
}
