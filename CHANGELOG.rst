Changelog
=========

Developing
----------

Changed
~~~~~~~

* Migrate from Travis to Github Actions. (improvement)

* Upgrade to pip 20.3.3

Fixed
~~~~~

* Fix unreachable join when an inbound task fails as defined in the task transition. (bug fix)
* Throw exception if the workflow definition that is written in YAML contains duplicate keys
  (i.e. task name). (bug fix)

1.3.0
-----

Added
~~~~~

* Implement the orquesta-rehearse command to run unit tests for workflow. (new feature, beta)
  Contributed by AJ (guzzijones)

Changed
~~~~~~~

* Remove mistral fixtures because they were used as ref to support multiple specs. Mistral is
  deprecated in StackStorm and there's no intention to support it here. A mistral to orquesta
  workflow conversion tool is available at https://github.com/StackStorm/orquestaconvert.

Fixed
~~~~~

* Fix the custom flake8 extensions to check import statements. (bug fix)
* Fix the deprecation warning that flags are not at the start of the expression. (bug fix)

1.2.0
-----

Changed
~~~~~~~

* Run pep8 and docs in tox with python3.
* Use black https://pypi.org/project/black/ for code formatting.
* Update tox to return error if there are uncommitted schema changes.

Fixed
~~~~~

* Warn users when there is a loop and no start task identified. (bug fix)
* Lock global variables during initialization to make them thread safe. (bug fix)
* Workflow stuck in running if one or more items failed in a with items task. (bug fix)
* Fix use case where a failed with items task is run again if the task is in a cycle. (bug fix)

1.1.1
-----

Fixed
~~~~~

* Fix task retry where transition on error is also executed along with retry. (bug fix)

1.1.0
-----

Added
~~~~~

* Add feature to retry task execution on given condition with delay in between retries and
  max number of retries. (new feature)
  Contributed by Hiroyasu Ohyama (@userlocalhost) and Nick Maludy (@nmaludy)
* Add support to rerun completed workflow (failed or succeeded) from given task(s). (new feature)

Changed
~~~~~~~

* Replace "noop" with "continue" when "do" is not specified. The new "continue" command
  will not alter the previous task state and will continue to conduct the workflow
  execution. StackStorm/st2#4740 (improvement)
* Refactor conductor to not store each item result in task state. If there are a lot of items
  and/or result size is huge per item, then there will be a performance impact on database
  write operations when recording the conductor state. (improvement)
* Use ujson to deepcopy dict(s) for faster performance. (improvement)
* Refactor how inbound criteria for join task is evaluated to count by task completion
  instead of task transition. (improvement)

Fixed
~~~~~

* Fix conducting of cycle with a fork. Fixes #169 (bug fix)
* Fix request_workflow_status to ignore certain status change errors such as pausing a workflow
  that is already pausing and canceling a workflow that is already canceling. (bug fix)
* Remove rendering of workflow output automatically when updating task state. This caused
  workflow output to render incorrectly in certain use case. The render_workflow_output function
  must be called separately. (bug fix)
* When inspecting custom YAQL/Jinja function to see if there is a context arg, use getargspec
  for py2 and getfullargspec for py3. (bug fix)
* Check syntax on with items task to ensure action is indented correctly. Fixes #184 (bug fix)
* Fix variable inspection where ctx().get() method calls are identified as errors.
  Fixes StackStorm/st2#4866 (bug fix)
* Fix a problem of TypeError orccuring when a list (or dict) value that contains unhashable typed
  value (list or dict) is passed in some YAQL operators (e.g. distinct()). Fixes #176 (bug fix)
  Contributed by Hiroyasu Ohyama (@userlocalhost)

1.0.0
-----

Changed
~~~~~~~

* Change the version number to the semver format and from 0.6 -> 1.0.0 to indicate GA.
* Rephrased the error message for the unreachable join task. Fixes #162 (improvement)

Fixed
~~~~~

* Allow tasks in the same transition with a "fail" command to run. (bug fix)
* Fix Jinja block expression to render correctly. (bug fix)

0.5
---

Added
~~~~~

* Add flake8 extension to restrict import alias. (improvement)
* Add developer docs on getting started, testing, and StackStorm integration. (improvement) 

Changed
~~~~~~~

* Refactor concept of task flow to workflow and task state. (improvement)
* Restrict ctx function from returning internal vars. (improvement)

Fixed
~~~~~

* Fix conductor performance for complex workflow definition. (bug fix)
* Fix overwritten context variables on task join. (bug fix)
* Fix with items task stuck in running when item(s) failed. (bug fix)
* Fix task status for various scenarios on with item task. (bug fix)
* Fix return value of item that evaluate to false. (bug fix)
* Fix workflow stuck in resuming when pending task has transition error. (bug fix)

0.4
---

Added
~~~~~

* Add get_routes function to workflow graph to identify possible execution routes. (new feature)
* Add ascii art diagrams to docs to illustrate workflows with join task. (improvement)

Fixed
~~~~~

* Add sleep in while loop for composing execution graph to spread out cpu spike. (improvement) 
* Value in quotes in shorthand publish should be evaluated as string type. Fixes #130 (bug fix)
* Fix interpretation of boolean value in shorthand format of publish. Fixes #119 (bug fix)
* Update YAQL section in docs on use of "=>" for named parameters in function calls. Closes #124
* Fix with items intepretor to handle variables that contain the word 'in'. (bug fix)
  Contributed by Anton Kayukov (@batk0)

0.3
---

Added
~~~~~

* Add with items model to the orquesta task spec. (improvement)
* Add delay attribute to the orquesta task spec. (improvement)
* Add script to generate JSON schema from the workflow models. (improvement)
* Add command to make package for upload to pypi. (improvement)

Changed
~~~~~~~

* Allow workflow to output on other completed states such as error. (improvement)
* Allow multiple transition between two tasks. (improvement)
* Refactor finalize_context in task spec to get the transition precisely. (improvement)
* Refactor conductor log entries and methods. (improvement)
* Refactor rendering of task spec in conductor to support with items model. (improvement)

Fixed
~~~~~

* Fix state change when workflow output fails rendering. (bug fix)
* Fix vars and input that references app context. (bug fix)
* Convert strings in context to unicode to fix problems with mixing
  ascii and unicode strings in expressions. (bug fix)


0.2
---

Added
~~~~~

* Add pep8 checks on module imports and other coding styles. (improvement)
* Allow application to pass runtime context on workflow execution. (improvement)
* Log an error in the conductor when a failed execution event is received. (improvement)

Changed
~~~~~~~

* Rename project from orchestra to orquesta.
* Replace if else logic with state machines to handle state transition for
  task and workflow execution. (improvement)
* Refactor expression functions to not have to require the context argument. (improvement)
* Clean up conductor and mark some of the methods as private. (improvement)

Fixed
~~~~~

* Fix bug where current task is not set in the context when task spec is rendering. (bug fix)
* Fix bug where self looping task reference an outdated context. (bug fix)
* Fix bug where self looping task does not terminate. (bug fix)
