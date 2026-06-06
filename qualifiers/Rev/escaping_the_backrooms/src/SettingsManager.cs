using System.Collections.Generic;
using UnityEngine;

public class SettingsManager : MonoBehaviour {
	int resolutionOption = 0;
	bool fullscreen;

    private void Start() {
		
    }

	public void ChangeResolution(int value) {
		switch (resolutionOption) {
			case -1:
				if (resolutionOption > 0) resolutionOption--;
				else resolutionOption = 6;
				break;
            case 1:
                if (resolutionOption < 6) resolutionOption++;
                else resolutionOption = 0;
				break;
		}
	}
}
