using UnityEngine;

public struct PosRotData {
	public Vector3 pos;
	public Quaternion rot;

	public PosRotData(Vector3 pos, Quaternion rot) {
		this.pos = pos;
		this.rot = rot;
	}
}

public class ItemManager : MonoBehaviour {
	public static PosRotData[] originalTransforms = new PosRotData[10];
    PosRotData almond_water;
    PosRotData torch_light;
    PosRotData notebook;
    PosRotData goofy_notebook;
	PosRotData chips;

	public Transform handPivot;
    public GameObject hand;
	public GameObject dropEmpty;

	public static GameObject[] hotbarItems = { null, null, null };
	public static int[] hotbarItemsUID = { 0, 0, 0 };
	public static int hotbarSlot;

	public static bool debug = true;

    public static void Clear() {
        hotbarItems[0] = hotbarItems[1] = hotbarItems[2] = null;
    }

	private void Start() {
		hotbarSlot = 0;
		
		torch_light = new PosRotData(
            new Vector3(0, 0, 0),
            new Quaternion(0, 0, 0, 1)
        );

        almond_water = new PosRotData(
            new Vector3(0, 0, 0),
            new Quaternion(-0.5f, 0.5f, 0.5f, 0.5f)
        );

        goofy_notebook = new PosRotData(
            new Vector3(0, 0, -0.15f),
            new Quaternion(0, 0, -0.707106829f, 0.707106829f)
        );

        notebook = new PosRotData(
            new Vector3(0, 0, -0.15f),
            new Quaternion(0, 0, -0.707106829f, 0.707106829f)
        );

		chips = new PosRotData(
			new Vector3(-0.15f, 0, 0),
			new Quaternion(0, 1, 0, 0)
		);

		originalTransforms[0] = torch_light;
        originalTransforms[1] = almond_water;
		originalTransforms[2] = goofy_notebook;
        originalTransforms[3] = notebook;
        originalTransforms[4] = chips;
    }

    private void OnGUI() {
		if (!debug) return;
        GUI.Label(new Rect(10, 1, 300, 300), "Debug:");
        GUI.Label(new Rect(10, 31, 300, 300), hotbarSlot.ToString());
		GUI.Label(new Rect(10, 46, 300, 300),
			string.Format("[{0}, {1}, {2}]", hotbarItems[0], hotbarItems[1], hotbarItems[2])
		);

        GUI.Label(new Rect(10, 60, 300, 300), string.Format("Amp: {0}, Freq: {1}", HeadBob.amplitude, HeadBob.frequency));


        if (hit.collider == null) {
			GUI.Label(new Rect(10, 16, 300, 300), "not hit");
			return;
		}

		GUI.Label(new Rect(10, 16, 300, 300), "hit: " + hit.collider.gameObject.layer);
    }

    RaycastHit hit;
	Outline outline;
	bool highlight;

	private void Update() {
        Ray ray = Player.shared.playerCamera.ScreenPointToRay(Input.mousePosition);
		
		if (!highlight && outline != null) {
			outline.enabled = false;
			outline.OutlineMode = Outline.Mode.OutlineHidden;
		}

		// Layermask 9: Item
		// 512 = 1 << 9
		if (Physics.Raycast(ray, out hit, 2, 512)) {
			Collider collider = hit.collider;
			outline = collider.GetComponent<Outline>();
			outline.enabled = true;
			outline.OutlineMode = Outline.Mode.OutlineAll;
			highlight = true;

			if (Input.GetKeyDown(KeyCode.F) && hotbarItems[hotbarSlot] == null) {
                outline.enabled = false;
                outline.OutlineMode = Outline.Mode.OutlineHidden;
                Item item = collider.GetComponent<Item>();
				Rigidbody r = item.GetComponent<Rigidbody>();
				r.isKinematic = true;
				r.useGravity = false;
				Item collectedItem = Instantiate(item, hand.transform.position, Quaternion.identity, hand.transform);
				collectedItem.transform.SetLocalPositionAndRotation(
					originalTransforms[item.ID].pos, originalTransforms[item.ID].rot
				);
				hotbarItems[hotbarSlot] = collectedItem.gameObject;
				Destroy(collider.gameObject);
			}
		} else highlight = false;

		if (Input.GetKeyDown(KeyCode.V) && hotbarItems[hotbarSlot] != null) {
			GameObject item = hotbarItems	[hotbarSlot];
			GameObject clone = Instantiate(item, dropEmpty.transform.position, dropEmpty.transform.rotation);

			Destroy(item);
			
			Rigidbody rigidBody	= clone.GetComponent<Rigidbody>();
            rigidBody.useGravity = true;
			rigidBody.isKinematic = false;
			rigidBody.WakeUp();

			if (hotbarItems[hotbarSlot] != null) // -1 is air
				hotbarItems[hotbarSlot] = null;
		}

		
        if (Input.mouseScrollDelta.y > 0) {
            hotbarSlot++;
            if (hotbarSlot > 2) hotbarSlot = 0;
			handPivot.localRotation = Quaternion.Euler(60, 0, 0);

        }

        if (Input.mouseScrollDelta.y < 0) {
			hotbarSlot--;
			if (hotbarSlot < 0) hotbarSlot = 2;
            handPivot.localRotation = Quaternion.Euler(60, 0, 0);
        }

        SwitchItem(hotbarSlot);
	}
	public void SwitchItem(int slot) {
		for (int i = 0; i < 3; i++)
			if (hotbarItems.Length > i && hotbarItems[i] != null)
				hotbarItems[i].SetActive(i == slot);
	}
}
