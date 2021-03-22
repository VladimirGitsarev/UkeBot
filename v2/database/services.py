from database.models import Favorite

class DBServices:

    @staticmethod
    def check_liked(user_id, cur_song, db_session):
        return db_session.query(Favorite).filter(
            Favorite.user_id == str(user_id),
            Favorite.url == cur_song['url']
        ).count()

    @staticmethod
    def add_song_to_favorites(user_id, cur_song, db_session):
        new_favorite = Favorite(
            user_id=user_id,
            url=cur_song['url'],
            title=cur_song['title']
        )

        db_session.add(new_favorite)
        db_session.commit()

    @staticmethod
    def remove_song_from_favorites(user_id, cur_song, db_session):
        db_session.query(Favorite).filter(
            Favorite.user_id == str(user_id),
            Favorite.url == cur_song['url']
        ).delete()
        db_session.commit()


    @staticmethod
    def get_favorites(user_id, db_session):
        return db_session.query(Favorite).filter(Favorite.user_id == str(user_id)).order_by(-Favorite.id).all()
