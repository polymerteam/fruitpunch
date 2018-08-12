from django.conf.urls import url
from api.v1 import views


urlpatterns = [
    url(r'^users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserGet.as_view()),

    url(r'^products/$', views.ProductList.as_view()),
    url(r'^products/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view()),

    url(r'^recipes/$', views.RecipeList.as_view()),
    url(r'^recipes/create-with-ingredients/$', views.RecipeCreateWithIngredients.as_view()),
    url(r'^recipes/(?P<pk>[0-9]+)/$', views.RecipeDetail.as_view()),

    url(r'^ingredients/$', views.IngredientList.as_view()),
    url(r'^ingredients/(?P<pk>[0-9]+)/$', views.IngredientDetail.as_view()),

    url(r'^batches/$', views.BatchList.as_view()),
    url(r'^batches/(?P<pk>[0-9]+)/$', views.BatchDetail.as_view()),
    url(r'^batches/create-with-items/$', views.BatchCreateWithItems.as_view()),


    url(r'^batchitems/$', views.BatchItemList.as_view()),
    url(r'^batchitems/(?P<pk>[0-9]+)/$', views.BatchItemDetail.as_view()),

    url(r'^inventories/$', views.InventoryList.as_view()),


    url(r'^received/$', views.ReceivedInventoryList.as_view()),
    url(r'^received/(?P<pk>[0-9]+)/$', views.ReceivedInventoryDetail.as_view()),


    # url(r'^userprofiles/$', views.UserProfileList.as_view()),
    # url(r'^userprofiles/(?P<pk>[0-9]+)/$', views.UserProfileGet.as_view()),
    # url(r'^users/$', views.UserList.as_view()),
    # url(r'^users/(?P<pk>[0-9]+)/$', views.UserGet.as_view()),
    # url(r'^userprofiles/$', views.UserProfileList.as_view()),
    # url(r'^userprofiles/(?P<pk>[0-9]+)/$', views.UserProfileGet.as_view()),
    # url(r'^userprofiles/edit/(?P<pk>[0-9]+)/$', views.UserProfileEdit.as_view()),
    # url(r'^userprofiles/clear-token/(?P<pk>[0-9]+)/$', views.UserProfileClearToken.as_view()),
    # url(r'^userprofiles/last-seen/(?P<pk>[0-9]+)/$', views.UserProfileLastSeenUpdate.as_view()),
    # url(r'^userprofiles/increment-walkthrough/(?P<pk>[0-9]+)/$', views.UserProfileIncrementWalkthroughUpdate.as_view()),
    # url(r'^userprofiles/complete-walkthrough/(?P<pk>[0-9]+)/$', views.UserProfileCompleteWalkthroughUpdate.as_view()),

    # url(r'^users/create/$', views.UserProfileCreate.as_view(), name='create_userprofile'),
    # url(r'^userprofiles/change-username-password/(?P<pk>[0-9]+)/$', views.UserChangeUsernamePassword.as_view()),

    # url(r'^teams/$', views.TeamList.as_view()),
    # url(r'^teams/(?P<pk>[0-9]+)/$', views.TeamGetAndEdit.as_view()),
    # url(r'^teams/create/$', views.TeamCreate.as_view(), name='create_team'),

    # url(r'^$', views.index, name='index'),
    
    # url(r'^tasks/create/$', views.TaskCreate.as_view(), name='create_task'),
    # url(r'^tasks/create-with-output/$', views.TaskCreateWithOutput.as_view()),

    # url(r'^tasks/$', views.TaskList.as_view(), name='tasks'),
    # url(r'^tasks/(?P<pk>[0-9]+)/$', views.TaskDetail.as_view(), name='task_detail'),
    # url(r'^tasks/edit/(?P<pk>[0-9]+)/$', views.TaskEdit.as_view()),
    # url(r'^tasks/search/$', views.TaskSearch.as_view()),
    # url(r'^tasks/simple/$', views.SimpleTaskSearch.as_view()),
    # url(r'^tasks/delete/(?P<pk>[0-9]+)/$', views.DeleteTask.as_view()),

    # url(r'^files/$', views.FileList.as_view(), name='files'),

    # url(r'^items/create/$', views.CreateItem.as_view(), name='create_item'),
    # url(r'^items/$', views.ItemList.as_view()),
    # url(r'^items/(?P<pk>[0-9]+)/$', views.ItemDetail.as_view()),

    # url(r'^inputs/create/$', views.CreateInput.as_view(), name='create_input'),
    # url(r'^inputs/create-without-amount/$', views.CreateInputWithoutAmount.as_view()),
    # url(r'^inputs/(?P<pk>[0-9]+)/$', views.InputDetail.as_view()),

    # url(r'^processes/$', views.ProcessList.as_view(), name='process_types'),
    # url(r'^processes/(?P<pk>[0-9]+)/$', views.ProcessDetail.as_view(), name='process_type_detail'),
    # url(r'^processes/duplicate/$', views.ProcessDuplicate.as_view(), name='process_duplicate'),


    # url(r'^products/$', views.ProductList.as_view(), name='product_types'),
    # url(r'^products/(?P<pk>[0-9]+)/$', views.ProductDetail.as_view(), name='product_type_detail'),
    # url(r'^products/codes/$', views.ProductCodes.as_view()),

    # url(r'^attributes/$', views.AttributeList.as_view(), name='attributes'),
    # url(r'^attributes/(?P<pk>[0-9]+)/$', views.AttributeDetail.as_view(), name='attribute_detail'),
    # url(r'^attributes/move/(?P<pk>[0-9]+)/$', views.ReorderAttribute.as_view(), name='attribute_move'),

    # url(r'^taskAttributes/$', views.TaskAttributeList.as_view()),
    # url(r'^taskAttributes/(?P<pk>[0-9]+)/$', views.TaskAttributeDetail.as_view()),

    # url(r'^movements/create/$', views.MovementCreate.as_view(), name='create_movement'),
    # url(r'^movements/$', views.MovementList.as_view()),
    # url(r'^movements/(?P<pk>[0-9]+)/$', views.MovementReceive.as_view()),

    # url(r'^inventory/$', views.InventoryList.as_view()),
    # url(r'^inventory/detail/$', views.InventoryDetail.as_view()),
    # url(r'^inventory/detail-test/$', views.InventoryDetailTest2.as_view()), # this is the one in production!!!!

    # url(r'^activity/$', views.ActivityList.as_view(), name='activity_log'),
    # url(r'^activity/detail/$', views.ActivityListDetail.as_view()),

    # url(r'^goals/$', views.GoalList.as_view(), name='goals'),
    # url(r'^goals/(?P<pk>[0-9]+)/$', views.GoalGet.as_view()),
    # url(r'^goals/create/$', views.GoalCreate.as_view(), name='create_goal'),
    # url(r'^goals/edit/(?P<pk>[0-9]+)/$', views.GoalRetrieveUpdateDestroy.as_view(), name='goal_edit'),
    # url(r'^goals/move/(?P<pk>[0-9]+)/$', views.ReorderGoal.as_view(), name='goal_move'),

    # url(r'^pins/$', views.PinList.as_view(), name='pins'),
    # url(r'^pins/create/$', views.PinCreate.as_view(), name='create_pin'),
    # url(r'^pins/edit/(?P<pk>[0-9]+)/$', views.PinRetrieveUpdateDestroy.as_view(), name='pin_edit'),

    # url(r'^alerts/$', views.AlertList.as_view()),
    # url(r'^alerts/(?P<pk>[0-9]+)/$', views.AlertGet.as_view()),
    # url(r'^alerts/create/$', views.AlertCreate.as_view()),
    # url(r'^alerts/edit/(?P<pk>[0-9]+)/$', views.AlertEdit.as_view()),
    # url(r'^alerts/mark-as-read/$', views.AlertsMarkAsRead.as_view()),

    # url(r'^alerts/recently-flagged-tasks/$', views.GetRecentlyFlaggedTasks.as_view()),
    # url(r'^alerts/recently-unflagged-tasks/$', views.GetRecentlyUnflaggedTasks.as_view()),
    # url(r'^alerts/incomplete-goals/$', views.GetIncompleteGoals.as_view()),
    # url(r'^alerts/complete-goals/$', views.GetCompleteGoals.as_view()),
    # url(r'^alerts/recent-anomolous-inputs/$', views.GetRecentAnomolousInputs.as_view()),

    # url(r'^adjustments/$', views.CreateAdjustment.as_view(), name='adjustments'),

    # url(r'^inventories/$', views.InventoryList2.as_view(), name='inventories'),
    # url(r'^inventories/aggregate/$', views.InventoryList2Aggregate.as_view(), name='inventories-aggregate'),

    # url(r'^adjustment-history/$', views.AdjustmentHistory.as_view(), name='adjustment-history'),

    # url(r'^recipes/$', views.RecipeList.as_view(), name='recipes'),
    # url(r'^recipes/(?P<pk>[0-9]+)/$', views.RecipeDetail.as_view(), name='recipe_detail'),
    # url(r'^ingredients/$', views.IngredientList.as_view(), name='ingredients'),
    # url(r'^ingredients/(?P<pk>[0-9]+)/$', views.IngredientDetail.as_view(), name='ingredient_detail'),
    # url(r'^ingredients/bulk-create/$', views.ingredient_bulk_create, name='ingredient_bulk_create'),
    # url(r'^taskIngredients/$', views.TaskIngredientList.as_view(), name='task_ingredients'),
    # url(r'^taskIngredients/(?P<pk>[0-9]+)/$', views.TaskIngredientDetail.as_view(), name='task_ingredient_detail'),
]

