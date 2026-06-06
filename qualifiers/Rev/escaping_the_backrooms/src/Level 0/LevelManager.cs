using UnityEngine;
using UnityEngine.Rendering.PostProcessing;

public class LevelManager : MonoBehaviour {
    public PostProcessVolume current_volume;

    public void Blur() {
        DepthOfField d;
        current_volume.profile.TryGetSettings(out d);
        d.focusDistance.value = Mathf.Lerp(d.focusDistance.value, 0.1f, 6.5f * Time.deltaTime);
        d.focalLength.value = Mathf.Lerp(d.focalLength.value, 112f, 6f * Time.deltaTime);
    }

    public void Unblur() {
        DepthOfField d;
        current_volume.profile.TryGetSettings(out d);
        d.focusDistance.value = Mathf.Lerp(d.focusDistance.value, 10, 3f * Time.deltaTime);
        d.focalLength.value = Mathf.Lerp(d.focalLength.value, 32, 6f * Time.deltaTime);
    }
}
