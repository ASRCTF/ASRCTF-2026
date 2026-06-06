using System.Collections;
using TMPro;
using UnityEngine;
using UnityEngine.SceneManagement;

public class MenuManager : MonoBehaviour {
	public static MenuManager instance;
	private int activeMenu = 0;

	public GameObject menu;
	public GameObject multiplayerMenu;
	public GameObject loadingScreen;
	public GameObject GUI;

	public TMP_Text playText;
	public TMP_Text settingsText;
	public TMP_Text quitText;

	public TMP_Text singleplayerText;
	public TMP_Text multiplayerText;
	public TMP_Text multiplayerReturnText;

	public GameObject playerPrefab;
	public static Vector3 spawnLocation = new(2.985f, 1f, -0.6f);

    private void Awake() {
        if (instance == null) instance = this;
    }

    public void StartGame() {
		Instantiate(playerPrefab, spawnLocation, Quaternion.identity);
		Destroy(Camera.main.gameObject);
        Cursor.lockState = CursorLockMode.Locked;
    }

    public void ButtonPlay() {
        menu.SetActive(false);
		activeMenu = 1;
		multiplayerMenu.SetActive(true);
    }

	public void ButtonSingleplayer() {
		multiplayerMenu.SetActive(false);
		EnterGame();
	}

	public void ButtonMultiplayer() {

	}

	public void ButtonReturn() {
		multiplayerMenu.SetActive(false);
		menu.SetActive(true);
		activeMenu = 0;
	}

	public void EnterGame() {
        Camera.main.GetComponent<Animator>().Play("Camera");
        StartCoroutine(Transition());
    }

	IEnumerator Transition() {
		yield return new WaitForSeconds(3f);
		StartGame();
    }

	public void ButtonSettings() {
		// TODO: Settings
	}

	public void ButtonQuit() {
		Application.Quit();
		// TODO: Quit Animation or smth
	}

	void ResetText() {
        switch (activeMenu) {
			case 0:
                playText.text = "Play";
                settingsText.text = "Settings";
                quitText.text = "Quit";
                playText.color = Color.white;
                settingsText.color = Color.white;
                quitText.color = Color.white;
                break;

			case 1:
                singleplayerText.text = "Singleplayer";
                multiplayerText.text = "Multiplayer";
                multiplayerReturnText.text = "Return";
                singleplayerText.color = Color.white;
                multiplayerText.color = Color.white;
                multiplayerReturnText.color = Color.white;
                break;

			default:
				Debug.LogError("Invalid Menu!");
				break;
		}
    }

	public void UnHover() {
        ResetText();
    }

	public void Hover(int hoveredButton) {
		ResetText();

		switch (hoveredButton) {

			// Main Menu:
			case 0:
				playText.text = "> Play <";
				playText.color = Color.yellow;
				break;
			case 1:
				settingsText.text = "> Settings <";
				settingsText.color = Color.yellow;
				break;
			case 2:
				quitText.text = "> Quit <";
				quitText.color = Color.yellow;
				break;

			// Multiplayer Menu
			case 3:
				singleplayerText.text = "> Singleplayer <";
				singleplayerText.color = Color.yellow;
				break;
			case 4:
				multiplayerText.text = "> Multiplayer <";
                multiplayerText.color = Color.yellow;
                break;
			case 5:
                multiplayerReturnText.text = "> Return <";
                multiplayerReturnText.color = Color.yellow;
                break;
		}
	}

	public static bool allowTeleport = false;

    void FixedUpdate() {
		if (Player.shared != null)
		if (Player.shared.playerCamera.transform.position.y < -10) {
			if (allowTeleport) {
                ItemManager.Clear();
                loadingScreen.SetActive(true);
                SceneManager.LoadSceneAsync(1);
                allowTeleport = false;
            }
		}
    }
}
