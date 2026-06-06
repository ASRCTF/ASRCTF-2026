using UnityEngine;

public class GUIManager : MonoBehaviour {
    Color32 color = new Color32(255, 255, 255, 50);

	private void OnGUI() {
        // Draws Stamina Bar
        Texture2D texture = new Texture2D(1, 1);
        texture.SetPixel(0, 0, color);
        texture.Apply();
        GUI.skin.box.normal.background = texture;
        GUI.Box(new Rect(0, Screen.height + 0.7f, Screen.width * (Player.shared.stamina / 7), 1), texture);
    }
}
