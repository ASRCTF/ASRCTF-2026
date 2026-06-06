using UnityEngine;

public class AlmondWater : Item {
    void Update() {
        if (ItemManager.hotbarItems[ItemManager.hotbarSlot].GetComponent<Item>().ID != ID)
            return; 

        if (Input.GetMouseButtonDown(0)) {

        }
    }
}
