using UnityEngine;
using UnityEngine.SceneManagement;

public class Exit_Door : MonoBehaviour {
    bool loading = false;

    void OnTriggerEnter(Collider other) {
        Debug.Log(other.gameObject.name);
        if (other.transform.gameObject == Player.shared.capsule) {
            Debug.Log("Triggered exit door");
            Player.shared.gameOverScreen.SetActive(true);
            Player.shared.lockMovement = true;
            Player.shared.timingText.enabled = false;
        }
    }

    private void FixedUpdate() {
        if (Player.shared.gameOverScreen.active && Input.GetKeyDown(KeyCode.E) && !loading) {
            if (Player.shared.timeElapsed > 10f) {
                Player.shared.timeElapsed = 0f;
                loading = true;
                Player.shared.loadingScreen.SetActive(true);
                Player.shared.gameOverScreen.SetActive(false);
                Cursor.lockState = CursorLockMode.None;
                SceneManager.LoadSceneAsync("Map");
            } else {
                Player.shared.winScreen.SetActive(true);
            }
        }
    }
}