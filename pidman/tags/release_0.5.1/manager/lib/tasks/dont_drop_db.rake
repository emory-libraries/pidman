# dropping the database destroys the functions so we dont want to drop the db
Rake::TaskManager.class_eval do
  def delete_task(task_name)
    @tasks.delete(task_name.to_s)
  end
  Rake.application.delete_task("db:test:purge")
end
namespace :db do
    namespace :test do
        task :purge => [:environment] do
            #ActiveRecord::Migrator.migrate("db/migrate/", 0)
        end
    end
end