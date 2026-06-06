using UnityEngine;

public class HeadBob : MonoBehaviour {
	[SerializeField] bool _enabled = true;

	public static float amplitude;
	public static float frequency = 1;
	public Transform handPivot;

	float bobSpeed = 14f;
	[SerializeField]
	float defaultPosY = 3.05f;
	float timer = 0f;

	float tiltAngle = 20f;
	public Transform peekOrigin;
	public Transform peekLeft;
	public Transform peekRight;

	public Transform crawlDown;

    private void Update() {
		// Bruh this took me 2hrs to figure out :skull:
		// Head Tilt
		if (Input.GetKey(KeyCode.Q)) {
			transform.position = Vector3.Lerp(transform.position, peekLeft.position, 6.5f * Time.deltaTime);
			Player.shared.cameraRotZ = Mathf.Lerp(Player.shared.cameraRotZ, tiltAngle, 6.5f * Time.deltaTime);
		} else {
			transform.position = Vector3.Lerp(transform.position, peekOrigin.position, 6.5f * Time.deltaTime);	
			Player.shared.cameraRotZ = Mathf.Lerp(Player.shared.cameraRotZ, 0, 6.5f * Time.deltaTime);
		}
		
		if (Input.GetKey(KeyCode.E)) {
			transform.position = Vector3.Lerp(transform.position, peekRight.position, 6.5f * Time.deltaTime);
			Player.shared.cameraRotZ = Mathf.Lerp(Player.shared.cameraRotZ, -tiltAngle, 6.5f * Time.deltaTime);
		} else {
			transform.position = Vector3.Lerp(transform.position, peekOrigin.position, 6.5f * Time.deltaTime);
			Player.shared.cameraRotZ = Mathf.Lerp(Player.shared.cameraRotZ, 0, 6.5f * Time.deltaTime);
		}

		// Handle crouch
		if (Input.GetKey(KeyCode.C)) {
			defaultPosY = Mathf.Lerp(defaultPosY, crawlDown.position.y - 1, 6.5f * Time.deltaTime);
			Player.shared.controller.center = new(0, -0.5f, 0);
			Player.shared.controller.height = 1f;
			Player.shared.isCrouching = true;
			Player.shared.speed = Player.shared.walkSpeed;
            amplitude = 0.10f;
            frequency = 0.6f;
        }
		else {
			defaultPosY = Mathf.Lerp(defaultPosY, 0.7f, 6.5f * Time.deltaTime);
			Player.shared.controller.center = new(0, 0, 0);
			Player.shared.controller.height = 2;
            Player.shared.isCrouching = false;
        }

        handPivot.localPosition = new(handPivot.localPosition.x, defaultPosY, handPivot.localPosition.z);
		handPivot.rotation = Quaternion.Slerp(handPivot.rotation, transform.rotation, 7.5f * Time.deltaTime);

		if (!_enabled) return;
		Vector3 velocity = Player.velocity;
		Vector3 localPos = transform.localPosition;
		if (velocity.x != 0 && velocity.z != 0) {
			timer += Time.deltaTime * bobSpeed;
			transform.localPosition = new(
				localPos.x, amplitude * Mathf.Sin(timer * frequency) + defaultPosY, localPos.z
			);
		} else {	
			timer = 0;
			transform.localPosition = new(
				localPos.x, Mathf.Lerp(localPos.y, defaultPosY, bobSpeed * Time.deltaTime
				), localPos.z
			);
		}
	}
}