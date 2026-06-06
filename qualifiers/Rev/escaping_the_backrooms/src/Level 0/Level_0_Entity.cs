using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Video;

public class Level_0_Entity : MonoBehaviour {
	public Animator animator;
	public Transform player;
	public AudioSource audioSource;

	float growlCoolDown = 0f;
	NavMeshAgent agent;

	public Transform headTransform;
	public Vector3 spawnPos;
	public Vector3 playerSpawnPos;

	Vector3 direction;
	Vector3 posDifference;
	float distance;
	bool killing = false;

	VideoPlayer videoPlayer;

	void Awake() {
        agent = GetComponent<NavMeshAgent>();
		agent.destination = player.position;
	}

	void Start() {
        videoPlayer = Player.shared.playerCamera.GetComponent<VideoPlayer>();
    }

	void FixedUpdate() {
		growlCoolDown += Time.deltaTime;
		agent.destination = player.position;

		if (agent.velocity.magnitude > 0)
			animator.SetBool("Walking", true);
		else
			animator.SetBool("Walking", false);
		
		if (agent.remainingDistance < 100) {
			agent.speed = 2f;
			animator.speed = 1f;
		} else {
			animator.speed = 0.5f;
			return;
		}

		RaycastHit hit;
		posDifference = (player.position - transform.position);

        direction = posDifference.normalized;
		distance = posDifference.magnitude;

        // If entity is within 20m distance and can see you, it will speed.
        if (distance < 20 &&
			Physics.Raycast(transform.position, direction, out hit, 15) &&
			hit.collider.gameObject == player.gameObject &&
			growlCoolDown > 5 &&
			!killing
		) {
			growlCoolDown = 0f;
			agent.speed = 4.1f;
			audioSource.Play();
			Player.shared.glitchManager.glitch = true;
        }

		// Killing
        if (!killing && distance < 2) {
            Player.shared.lockMovement = true;
			Player.shared.death = true;
			Player.shared.entityPos = headTransform.position;

            agent.isStopped = true;
			agent.velocity = Vector3.zero;

            killing = true;
            audioSource.Stop();
            animator.Play("Kill");
        }
    }
		
	public void RespawnPlayer() {
		videoPlayer.enabled = true;
		videoPlayer.Play();
		videoPlayer.loopPointReached += VideoDone;

		transform.position = spawnPos;
		killing = false;
		Player.shared.capsule.transform.position = playerSpawnPos;
        Player.shared.lockMovement = false;
	}

	void VideoDone(VideoPlayer vp) {
		videoPlayer.enabled = false;
		agent.isStopped = false;
	}
}
