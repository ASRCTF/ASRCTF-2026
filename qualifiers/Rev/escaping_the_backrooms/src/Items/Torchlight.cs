using UnityEngine;
public class Torchlight : Item {
	public Light _light;
	public AudioSource _audio;

	void Update() {
		if (ItemManager.hotbarItems[ItemManager.hotbarSlot] == gameObject && Input.GetMouseButtonDown(0)) {
			_light.enabled = !_light.enabled;
			_audio.Play();
		}
	}
}
